# SpinningBikeProject
## Test Video Link
https://drive.google.com/file/d/1ofKwTssVWvjcTAJPS9sfAsZiZw3-Lw_y/view?usp=share_link

## 目前問題
路面轉彎角度和方向偵測\
方法一: \
segment -> Canny -> mask -> hough -> 找兩線交點 -> 找夾角
效果不彰\
\
方法二:\
segment -> Canny -> 找出邊緣的最高點\
\
方法三:\
segment -> findContours -> approxPolyDP -> (找出邊緣的最高點 / hough -> 找兩線交點 -> 找夾角)
還在嘗試\
\
想法四:\
segment -> findContours -> approxPolyDP -> hough -> 取左右兩邊的開始線段延伸 -> 找交點
