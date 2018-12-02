# ////////////////////////////////////
# // StockAndSentimentSystem:Stats
# //   ///////   ///////
# //  ///__  // ///__  //
# // | //  \__/|__/  \ //
# // |  //////    ///////
# //  \____  //  |___  //
# //  ///  \ // ///  \ //
# // |  ///////|  ///////
# //  \______/  \______/
# ////////////////////////////////////
import os
import sys
import glob


# ////////////////////////////////////
# //relating Directory
# ////////////////////////////////////
def del_all_files_in_dir(dir_path):
    """取得したディレクトリ内のすべてのファイルを削除する再帰的ではない

    Args:
        dir_path (string): 削除したいファイルが保管されているパス

    Returns:
        bool: True/False
    """
    rtn = False
    if(os.path.exists(dir_path)):
        try:
            os.chdir(dir_path)
            files_path = glob.glob("./*")
            for file_path in files_path:
                os.remove(file_path)
            rtn = True
        except:
            return rtn
    else:
        return rtn

    return rtn


def add_dot_dir_path(dir_path):
    """入力されたパスをチェックし、存在しなければディレクトリ名の前に[.(dot)]を付与する

    Args:
        dir_path (string): チェックするディレクトリのパス
    
    Returns:
        bool: False
        string: checked dir_path
    """
    if os.path.exists(dir_path):
        return dir_path
    else:
        dir_path = '.' + dir_path

    if os.path.exists(dir_path):
        return dir_path
    else:
        return False
