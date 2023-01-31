## サービス内容
Twitterのタイムラインを表示させるWebアプリ。<br>
複数デバイスで使用する際の利便性向上を目的としている。あるデバイスの画面で表示されているタイムラインと同一箇所が別のデバイスでも表示されるため、タイムラインを追いやすい。

※ 別デバイスでも同じTwitter IDでログインしておく必要がある。

### アプリリンク
https://j8851837.net<br><br>
以下にアクセスするとTwitterアカウント @j8851837 としてアプリにログインしたこととなる。<br>
https://j8851837.net/index_8851837/<br>
※ 上リンクからサイト訪問した全員が同一人物とみなされるため、意図しない挙動となる可能性がある

## 動作概要
### シーケンス図（ログイン前）
<img src='https://pbs.twimg.com/media/FnzTwY8aIAACyKC?format=jpg&name=medium' width="80%" height="80%">

### シーケンス図（ログイン後）
<img src='https://pbs.twimg.com/media/FnzTx0qaEAEzogw?format=jpg&name=medium' width="80%" height="80%">

### ブラウザからサーバーに送信する情報
<img src='https://pbs.twimg.com/media/FnzTzgSakAE3DLV?format=jpg&name=medium' width="80%" height="80%">

### 動作フロー図（フロント）
<img src='https://pbs.twimg.com/media/FnzT0ygaQAAJoB5?format=jpg&name=medium' width="80%" height="80%">

### 動作フロー図（バック）
<img src='https://pbs.twimg.com/media/FnzT2GHaMAMvTxF?format=jpg&name=medium' width="80%" height="80%">

### 工夫した点
- Twitter APIの利用回数は15分間で15回まで、一度の読み込みは100投稿までという制限があり、デバイスを切り替えるたびにAPIにアクセスすると制限を受ける可能性がある。動作フロー図に示した方法でAPIへのアクセス回数低減を図った。
  - 古い投稿を見るには、ページ下部までクロールすると100投稿追加で取得される(Ajax)。


## 使用技術
### フロントエンド
* **JavaScript**
  * 志望ポストの開発で使用されているSwiftやKtolinを使用したスマホアプリの作成も検討したが、スマホアプリ(特に私が使用するiPhoneのアプリ)だと審査が必要である。スピーディーに開発を行うため、Webアプリを開発することとした。

### バックエンド
* **Python**
  * 志望ポストの開発で使用されているため
  * 個人の開発でもこれまでに利用経験があるため
* **Django**
  * 志望ポストの開発で使用されているため
* **SQLite**
  * 個人開発であり、SQLサーバーを別で設ける手間を省くため

### インフラ
* **AWS(EC2)**
  * 志望ポストの本番環境ではおそらくAWSが使用されているだろうと予想し、学習のために使用した
  * （Dockerを使用しているが、Fargateを選択しなかったのは、EC2は無料で利用できるため）
* **Docker**
  *  多くの開発環境で使用されているという情報があり、学習のために使用した
* **NGINX**

### インフラ構成図
<img src='https://pbs.twimg.com/media/Fnzh7LjaMAA8FZo?format=png&name=900x900' width="50%" height="50%">

### ER図
<img src='https://pbs.twimg.com/media/FnzT3dtacAAkvWw?format=jpg&name=medium' width="50%" height="50%">

## テスト
Djangoのテストコード(test.py)を作成した。<br>
<img src='https://pbs.twimg.com/media/FnzndrtaQAAz0Sq?format=png&name=large' width="70%" height="70%"><br><br>
カバレッジは以下の通り。<br>
<img src='https://pbs.twimg.com/media/Fnzn9UpaUAEV3z0?format=png&name=900x900' width="50%" height="50%">
