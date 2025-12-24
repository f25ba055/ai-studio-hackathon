"""
ファイルアップロード処理
"""
import os
from config import Config
from PIL import Image
import io

class FileService:
    """ファイルアップロードに関するビジネスロジック"""

    def validate_image(self, file):
        """
        画像ファイルのバリデーション（拡張子偽装対策を含む）
        
        Args:
            file: アップロードされたファイルオブジェクト
            
        Returns:
            str: エラーメッセージ（問題がない場合はNone）
        """
        if not file or not file.filename:
            return None

        # 拡張子チェック（第1層の防御）
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in Config.ALLOWED_EXTENSIONS:
            return 'jpg, jpeg, png, gifのみ対応しています'

        # ファイルサイズチェック
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > Config.MAX_CONTENT_LENGTH:
            return '画像ファイルは5MB以下にしてください'

        # ファイルの実際の内容を検証（第2層の防御 - マジックナンバーチェック）
        try:
            # ファイルポインタを先頭に戻す
            file.seek(0)
            
            # Pillowで画像として開けるか試す
            img = Image.open(file)
            
            # 画像ファイルとして正しいか検証
            img.verify()
            
            # 再度開く（verifyの後はファイルが閉じられるため）
            file.seek(0)
            img = Image.open(file)
            
            # 許可された画像形式かチェック
            # PILのformatは大文字で返される（'JPEG', 'PNG', 'GIF'など）
            if img.format.upper() not in ['JPEG', 'PNG', 'GIF']:
                return f'対応していない画像形式です。jpg, jpeg, png, gifのみ対応しています。'
            
            # ファイルポインタを先頭に戻す（後で保存するため）
            file.seek(0)
            
            return None  # バリデーション成功
            
        except Exception as e:
            print(f"画像検証エラー: {e}")
            # ファイルポインタを戻しておく
            try:
                file.seek(0)
            except:
                pass
            return '有効な画像ファイルではありません。jpg, jpeg, png, gifのみ対応しています。'

    def save_review_photo(self, file, review_id):
        """
        レビュー写真を保存
        
        Args:
            file: アップロードされたファイルオブジェクト
            review_id: レビューID
            
        Returns:
            str: 保存されたファイル名（失敗時はNone）
        """
        try:
            # 画像のバリデーション（拡張子偽装対策を含む）
            validation_error = self.validate_image(file)
            if validation_error:
                print(f"バリデーションエラー: {validation_error}")
                return None
            
            file_ext = os.path.splitext(file.filename)[1].lower()
            filename = f'review_{review_id}{file_ext}'

            # 保存先ディレクトリの確認（存在しなければ作成）
            upload_dir = Config.UPLOAD_FOLDER
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir, exist_ok=True)

            # ファイル保存
            file_path = os.path.join(upload_dir, filename)
            file.seek(0)  # ファイルポインタを先頭に戻す
            file.save(file_path)
            
            # 保存後の最終検証（第3層の防御）
            try:
                with Image.open(file_path) as img:
                    img.verify()
                    # 再度開いて形式を確認
                with Image.open(file_path) as img:
                    if img.format.upper() not in ['JPEG', 'PNG', 'GIF']:
                        # 不正なファイルの場合は削除
                        os.remove(file_path)
                        print(f"保存後の検証失敗: 不正な画像形式 {img.format}")
                        return None
            except Exception as e:
                # 画像でない場合は削除
                if os.path.exists(file_path):
                    os.remove(file_path)
                print(f"保存後の検証失敗: {e}")
                return None

            return filename
            
        except Exception as e:
            print(f"ファイル保存エラー: {e}")
            return None

    def delete_review_photo(self, filename):
        """レビュー写真を削除"""
        if not filename:
            return True

        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                print(f"ファイル削除エラー: {e}")
                return False

        return True