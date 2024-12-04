# year_and_tax_adjustment

1. バージョン履歴
   * v1.0: 初版
   * v1.1: PDF ビューワーを作成

2. 備忘録
   1. バージョンファイルの作り方・適用方法
      1. `version.txt` ファイルでバージョン数を変える
      2. ターミナルで下記コマンドを実行する

      ```Bash
      create-version-file version.yaml --outfile app.version
      ```

      3. `pyinstaller 年末調整計算ツール.spec` を実行する

   2. `docs` の生成方法
      1. ターミナルで下記コマンドを実行する<br>
      `docs` ディレクトリに生成される

      ```Bash
      pdoc main.py -o docs
      ```
