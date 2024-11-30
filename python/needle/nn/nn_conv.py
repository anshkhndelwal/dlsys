
"""The module.
"""
from typing import List, Callable, Any
from needle.autograd import Tensor
from needle import ops
import needle.init as init
import numpy as np
from .nn_basic import Parameter, Module


class Conv(Module):
    """
    Multi-channel 2D convolutional layer
    IMPORTANT: Accepts inputs in NCHW format, outputs also in NCHW format
    Only supports padding=same
    No grouped convolution or dilation
    Only supports square kernels
    """
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, bias=True, device=None, dtype="float32"):
        super().__init__()
        if isinstance(kernel_size, tuple):
            kernel_size = kernel_size[0]
        if isinstance(stride, tuple):
            stride = stride[0]
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        
        self.weight = Parameter(init.kaiming_uniform(fan_in=(kernel_size ** 2) * in_channels,fan_out=(kernel_size ** 2) * out_channels,
            shape=(kernel_size, kernel_size, in_channels, out_channels),
            device=device,
            dtype=dtype
        ))
        self.padding = (kernel_size - 1) // 2
        if bias:
            self.bias = Parameter(init.rand(
                self.out_channels,
                low=-(1.0 / (in_channels * kernel_size ** 2) ** 0.5),
                high=1.0 / (in_channels * kernel_size ** 2) ** 0.5,
                device=device,
                dtype=dtype
            ))
        else:
            self.bias = None
        
        return

    def forward(self, x: Tensor) -> Tensor:

        output_nchw = ops.conv(
            ops.transpose(ops.transpose(x, (1, 2)), (2, 3)), 
            self.weight, 
            stride=self.stride, 
            padding=(self.kernel_size) // 2
        )
        if self.bias:
            output_nchw = output_nchw + self.bias.reshape((1, 1, 1, self.out_channels)).broadcast_to(output_nchw.shape)
        return ops.transpose(ops.transpose(output_nchw, (2, 3)), (1, 2))
        