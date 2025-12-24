"""
レビューデータへのアクセスを担当
"""
from repositories.database import get_db, close_db

class ReviewRepository:
    """レビューテーブルへのデータアクセス"""

    def find_by_spot_id(self, spot_id):
        """
        観光地IDからレビューを取得（N+1クエリ問題を解決）
        
        修正前: レビューのみ取得 → サービス層でユーザー情報をループで取得
        修正後: JOINを使ってレビューとユーザー情報を1回で取得
        """
        conn = get_db()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            
            # JOINを使ってレビューとユーザー情報を一度に取得
            cursor.execute('''
                SELECT 
                    r.review_id,
                    r.user_id,
                    r.spot_id,
                    r.review_content,
                    r.rating,
                    r.photo_filename,
                    r.created_at,
                    u.name as user_name
                FROM reviews r
                LEFT JOIN users u ON r.user_id = u.user_id
                WHERE r.spot_id = ?
                ORDER BY r.created_at DESC
            ''', (spot_id,))
            
            reviews = [dict(row) for row in cursor.fetchall()]
            return reviews
            
        except Exception as e:
            print(f"レビュー取得エラー: {e}")
            return []
        finally:
            close_db(conn)

    def find_by_id(self, review_id):
        """レビューIDからレビューを取得"""
        conn = get_db()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM reviews
                WHERE review_id = ?
            ''', (review_id,))
            
            review = cursor.fetchone()
            return dict(review) if review else None
            
        except Exception as e:
            print(f"レビュー取得エラー: {e}")
            return None
        finally:
            close_db(conn)

    def find_by_user_and_spot(self, user_id, spot_id):
        """ユーザーIDと観光地IDからレビューを取得（重複チェック用）"""
        conn = get_db()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM reviews
                WHERE user_id = ? AND spot_id = ?
            ''', (user_id, spot_id))
            
            review = cursor.fetchone()
            return dict(review) if review else None
            
        except Exception as e:
            print(f"レビュー取得エラー: {e}")
            return None
        finally:
            close_db(conn)

    def create(self, review_data):
        """レビューを作成"""
        conn = get_db()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reviews (user_id, spot_id, review_content, rating)
                VALUES (?, ?, ?, ?)
            ''', (
                review_data['user_id'],
                review_data['spot_id'],
                review_data['review_content'],
                review_data['rating']
            ))
            
            conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            print(f"レビュー作成エラー: {e}")
            conn.rollback()
            return None
        finally:
            close_db(conn)

    def update_photo_filename(self, review_id, photo_filename):
        """レビューに画像ファイル名を設定"""
        conn = get_db()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE reviews
                SET photo_filename = ?
                WHERE review_id = ?
            ''', (photo_filename, review_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"画像ファイル名更新エラー: {e}")
            conn.rollback()
            return False
        finally:
            close_db(conn)

    def delete(self, review_id):
        """レビューを削除"""
        conn = get_db()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM reviews
                WHERE review_id = ?
            ''', (review_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"レビュー削除エラー: {e}")
            conn.rollback()
            return False
        finally:
            close_db(conn)