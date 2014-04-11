from kivy.app import App
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line

from enum import IntEnum
from enum import Enum

from random import random

class Type(IntEnum):
    RIGHT_TOP = 1
    RIGHT_BOTTOM = 2
    LEFT_BOTTOM = 3
    LEFT_TOP = 4
    UNDEFINED = 5

class Direction(Enum):
    CLOCKWISE = 1
    COUNTER_CLOCKWISE = 2
    UNDEFINED = 3

class MyPaintWidget(Widget):
    circleShape = [Type.RIGHT_TOP, Type.RIGHT_BOTTOM, Type.LEFT_BOTTOM, Type.LEFT_TOP]
    editing = False
    bounds = []

    cX = 0
    cY = 0
    cD = 0
    
    def getType(self, dx, dy, direction):
        result = Type.UNDEFINED
        #print direction
        
        if direction != Direction.UNDEFINED:
            if dx > 0 and dy > 0:
                if (self.isClockwise(direction)):
                    result = Type.RIGHT_TOP
                else:
                    result = Type.LEFT_BOTTOM
            else:
                if dx < 0 and dy > 0:
                    if (self.isClockwise(direction)):
                        result = Type.RIGHT_BOTTOM
                    else:
                        result = Type.LEFT_TOP
                else:
                    if dx < 0 and dy < 0:
                        if (self.isClockwise(direction)):
                            result = Type.LEFT_BOTTOM
                        else:
                            result = Type.RIGHT_TOP
                    else:
                        if dx > 0 and dy < 0:
                            if (self.isClockwise(direction)):
                                result = Type.LEFT_TOP
                            else:
                                result = Type.RIGHT_BOTTOM

        print result

        return result

    def getPointsXAndY(self, points, index):
        startIndex = index * 2

        return [points[startIndex], points[startIndex + 1]]

    def isClockwise(self, direction):
        return direction == Direction.CLOCKWISE
            
    def isCircle(self, points, direction): 
        #print direction       
        #because the nature of the calculation of direction, the provided direction will be the opposite of what we need, so let's reverse it
        #direction = self.reverseDirection(direction)
        print direction

        result = False
        shape = self.circleShape
        STEP = 5
        index = 0
        startIndex = 0

        detected = [None] * 4

        currentPoint = self.getPointsXAndY(points, 0)
        currentType = None

        if direction != Direction.UNDEFINED:
            for x in range(STEP, len(points), STEP):
                try:
                    nextPoint = self.getPointsXAndY(points, x)
                except:
                    break

                #print nextPoint
                #print currentPoint

                dx = nextPoint[0] - currentPoint[0]
                dy = -(nextPoint[1] - currentPoint[1])

                if dx == 0 or dy == 0:
                    continue

                newType = self.getType(dx, dy, direction)

                # get the first item, or if the direction has changed
                if currentType is None or currentType != newType:
                    # if we have at least the first direction, check if the next direction is the next step in the circle drawing process
                    if currentType is not None:
                        if newType != shape[index]:
                                break

                    # a circle is a distionct set of drawing directions, so we need to follow them in order, from where the user started drawing
                    else:
                        index = shape.index(newType)
                        startIndex = index

                    self.bounds.insert(index, currentPoint)
                    
                    # don't double up on actions, because we need to compare lists
                    if detected.count(newType) == 0:
                        print index
                        #detected.insert(index, newType)
                        detected[index] = newType

                    # because we may start anywhere in the shape, we may need to do circular traversal of the shape array
                    if direction == Direction.CLOCKWISE:
                        index = (index + 1) % len(shape)
                    else:
                        index = (index - 1) % len(shape)

                currentType = newType
                currentPoint = nextPoint

                print shape
                print detected

                if shape == detected:
                    result = True
                    break

        return result

    def reverseDirection(self, direction):
        result = None

        if direction == Direction.UNDEFINED:
            result = direction
        else:
            if direction == Direction.CLOCKWISE:
                result = Direction.COUNTER_CLOCKWISE
            else:
                result = Direction.CLOCKWISE

        return result

    def determineDirection(self, points):
        result = Direction.UNDEFINED
        total = 0
        currentPoint = None
        previousPoint = None

        for i in range(0, len(points)/2, 1):
            currentPoint = self.getPointsXAndY(points, i)

            if previousPoint is not None:
                total += (currentPoint[0] - previousPoint[0]) * (currentPoint[1] + previousPoint[1])

            previousPoint = currentPoint

        if total > 0:
            result = Direction.CLOCKWISE
        else:
            if total < 0:
                result = Direction.COUNTER_CLOCKWISE

        return result
    
    def on_touch_down(self, touch):
        cD = 0
        editing = True
        color = (random(), 1., 1.)
        
        with self.canvas:
            Color(*color, mode='hsv')
            #d = 30.
            #Ellipse(pos=(touch.x - d/2, touch.y - d/2), size=(d,d,))
            touch.ud['line'] = Line(points=(touch.x, touch.y))

    def on_touch_move(self, touch):
        touch.ud['line'].points += [touch.x, touch.y]

    def on_touch_up(self, touch):
        editing = False
        direction = None

        if len(touch.ud['line'].points) > 0:
            points = touch.ud['line'].points

            if self.isCircle(points, self.determineDirection(points)):
                print "circle"
            else:
                self.cD = -1
                print "unknown"


class MindMapApp(App):
    
    def build(self):
        parent = Widget()
        painter = MyPaintWidget()
        clearbtn = Button(text='Clear')
        parent.add_widget(painter)
        parent.add_widget(clearbtn)
        
        def clear_canvas(obj):
            painter.canvas.clear()
        clearbtn.bind(on_release=clear_canvas)
        
        Config.set('input','multitouchscreen1','tuio,192.168.0.4:3333')
        return parent


if __name__ == '__main__':
    MyPaintApp().run()