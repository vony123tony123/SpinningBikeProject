# SpinningBikeProject
## Test Video Link
https://drive.google.com/drive/folders/1Sb6b0BC1J_1LKZ2U57y-wOMGemdH8yn_?usp=sharing

## 目前問題
路面轉彎角度和方向偵測\
方法一: \
segment -> Canny -> mask -> hough -> 找兩線交點 -> 找夾角
效果不彰\
\
方法二:\
segment -> Canny -> 找出邊緣的最高點\
效果比方法一好，但是入彎處會有問題(因為入彎處的曲線最高點可能不是道路尾端的點) \ 
\
方法三:\
segment -> findContours -> approxPolyDP -> (找出邊緣的最高點 / hough -> 找兩線交點 -> 找夾角)
還在嘗試\
\
想法四:\
segment -> findContours -> approxPolyDP -> hough -> 取左右兩邊的開始線段延伸 -> 找交點
