"""
レビューのビジネスロジック
"""
from repositories.review_repository import ReviewRepository
from services.file_service import FileService

class ReviewService:
    """レビューに関するビジネスロジック"""

    def __init__(self):
        self.review_repo = ReviewRepository()
        self.file_service = FileService()

    def get_reviews_by_spot(self, spot_id):
        """
        観光地のレビューを取得（N+1クエリ問題を解決）
        
        修正前: レビュー取得1回 + ユーザー名取得N回 = N+1回のクエリ
        修正後: JOINを使って1回のクエリで取得
        """
        # リポジトリ層でJOINを使ってユーザー情報も一緒に取得
        reviews = self.review_repo.find_by_spot_id(spot_id)
        
        # もうループでユーザー情報を取得する必要がない！
        # user_name は既にリポジトリ層で JOIN により取得済み
        
        return reviews

    def create_review(self, review_data):
        """レビューを作成（画像なし）"""
        # 必須フィールドチェック
        required_fields = ['user_id', 'spot_id', 'review_content', 'rating']
        for field in required_fields:
            if field not in review_data:
                return {'success': False, 'error': f'{field}が指定されていません'}

        # 文字数制限チェックがない（10万文字でも投稿可能）
        # 本来は len(review_data['review_content']) > 1000 などでチェックすべき

        # 重複チェック：既にレビューが存在する場合はエラー
        existing_review = self.review_repo.find_by_user_and_spot(
            review_data['user_id'],
            review_data['spot_id']
        )
        if existing_review:
            return {
                'success': False,
                'error': 'この観光地には既にレビューを投稿済みです。1つの観光地につき1つのレビューのみ投稿できます。'
            }

        # レビュー作成
        review_id = self.review_repo.create(review_data)

        if review_id:
            return {
                'success': True,
                'review_id': review_id,
                'message': 'レビューを投稿しました'
            }
        else:
            return {'success': False, 'error': 'レビューの作成に失敗しました'}

    def create_review_with_photo(self, request):
        """レビューを作成（画像あり）- トランザクション管理対応版"""
        # フォームデータの取得
        user_id = request.form.get('user_id')
        spot_id = request.form.get('spot_id')
        review_content = request.form.get('review_content')
        rating = request.form.get('rating')
        photo = request.files.get('photo')

        # 必須フィールドチェック
        if not all([user_id, spot_id, review_content, rating]):
            return {'success': False, 'error': '必須項目が不足しています'}

        # 重複チェック：既にレビューが存在する場合はエラー
        existing_review = self.review_repo.find_by_user_and_spot(user_id, spot_id)
        if existing_review:
            return {
                'success': False,
                'error': 'この観光地には既にレビューを投稿済みです。1つの観光地につき1つのレビューのみ投稿できます。'
            }

        # 画像のバリデーション
        if photo and photo.filename:
            validation_error = self.file_service.validate_image(photo)
            if validation_error:
                return {'success': False, 'error': validation_error}

        # レビュー作成
        review_data = {
            'user_id': user_id,
            'spot_id': spot_id,
            'review_content': review_content,
            'rating': rating
        }
        review_id = self.review_repo.create(review_data)

        if not review_id:
            return {'success': False, 'error': 'レビューの作成に失敗しました'}

        # 画像保存（トランザクション管理）
        photo_filename = None
        if photo and photo.filename:
            try:
                photo_filename = self.file_service.save_review_photo(photo, review_id)
                
                # 画像保存に成功した場合のみファイル名を更新
                if photo_filename:
                    self.review_repo.update_photo_filename(review_id, photo_filename)
                else:
                    # 画像保存に失敗した場合、レビューをロールバック
                    self.review_repo.delete(review_id)
                    return {
                        'success': False,
                        'error': '画像の保存に失敗しました。レビューは作成されませんでした。'
                    }
                    
            except Exception as e:
                print(f"画像保存エラー: {e}")
                # 例外が発生した場合、レビューをロールバック
                try:
                    self.review_repo.delete(review_id)
                except Exception as delete_error:
                    print(f"ロールバック中にエラーが発生: {delete_error}")
                
                return {
                    'success': False,
                    'error': f'画像の保存に失敗しました: {str(e)}'
                }

        return {
            'success': True,
            'review_id': review_id,
            'photo_filename': photo_filename,
            'message': 'レビューを投稿しました'
        }

    def delete_review(self, review_id, user_id):
        """レビューを削除（権限チェック付き）"""
        # レビューを取得
        review = self.review_repo.find_by_id(review_id)

        if not review:
            return {'success': False, 'error': 'レビューが見つかりません'}

        # 権限チェックがコメントアウトされている（他人のレビューも削除可能）
        # if review['user_id'] != int(user_id):
        #     return {'success': False, 'error': '他のユーザーのレビューは削除できません'}

        # 画像ファイルの削除処理が抜けている（ディスク容量を圧迫）
        # 画像ファイルがあれば削除
        # if review.get('photo_filename'):
        #     self.file_service.delete_review_photo(review['photo_filename'])

        # レビュー削除
        if self.review_repo.delete(review_id):
            return {
                'success': True,
                'message': 'レビューを削除しました'
            }
        else:
            return {'success': False, 'error': 'レビューの削除に失敗しました'}