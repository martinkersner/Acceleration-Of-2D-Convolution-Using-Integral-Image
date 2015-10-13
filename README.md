## Acceleration of 2D Convolution Using Integral Image

Martin Kersner, <m.kersner@gmail.com>

[Full text](https://dl.dropboxusercontent.com/u/13642345/Acceleration-of-2D-Convolution-Using-Integral-Image.pdf)

Computation time of box blur filter using convolution depends on the width of kernel. Wider kernels causes longer computation time. However, there is a method of calculating blurred image in constant time called integral image. Due to the constant reading of values, it was reached almost 800 times acceleration with this method. High order filters can be computed by repeated box filtering. This paper also deals with implementation details of acceleration of 2D convolution using
integral image.
