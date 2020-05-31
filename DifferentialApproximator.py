"""
DifferentialApproximator

Description: Use Euler's method to approximate a function's value based on derivative
"""
import math

def derivative(x, y):
    return math.e ** x

def pointSlopeEval(px, py, derivative, x):
    return (derivative * (x - px)) + py

dx = 0.1
targetX = 0.3
startX = 0.0
startY = 1.0
curX = startX
curY = startY

while curX < targetX:
    derv = derivative(curX, curY)
    curY = pointSlopeEval(curX, curY, derv, curX + dx)
    curX += dx
    
print("y=%.9f" % curY)
