from kivy.app import App
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Rectangle
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from enum import IntEnum
from enum import Enum

from random import random

class DeleteButton(Button):
    def __init__(self, position_hint=None, owner=None, **kwargs):
        super(DeleteButton, self).__init__(**kwargs)

        self.pos_hint = position_hint
        self.objectToDelete = owner

    def on_press(self):
        self.objectToDelete.parent.remove_widget(self.objectToDelete)

class Edge(FloatLayout):
    line = None
    selected = False
    deleteButton = None

    def __init__(self, vertexOne=None, vertexTwo=None, **kwargs):
        super(Edge, self).__init__(**kwargs)

        self.firstVertex = vertexOne
        self.secondVertex = vertexTwo

        self.drawLine()

    def drawLine(self):
        if self.line is not None:
            self.canvas.remove(self.line)

        with self.canvas:
            Color(.278, .498, 0) # rgb: 71, 127, 0
            self.line = Line(points=[self.firstVertex.center_x, self.firstVertex.center_y, self.secondVertex.center_x, self.secondVertex.center_y], width=2)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                pass
                #self.parent.remove_widget(self)
                    
        super(Edge, self).on_touch_down(touch)


class Vertex(ScatterLayout):
    MINIMUM_HEIGHT = 30
    TEXT_OFFSET = 40
    selected = False
    highlight = None
    edges = []

    defaultColour = (0, .278, .498, 1) # rgb: 0, 71, 127
    highlightColour = (.498, 0, .278, 1) #rgb: 127, 0, 71
    colour = defaultColour

    deleteButton = None

    def __init__(self, pos=None, size=None):
        super(Vertex, self).__init__()
        self.pos = pos
        self.size = size

        self.originalSize = size
        self.originalWidth = size[0]

        self.newIdea = TextInput(
            height = self.MINIMUM_HEIGHT,
            size_hint = (None, None),
            pos_hint = {'center_x':.5, 'center_y':.5},

            background_active = '',
            background_normal = '',

            use_bubble = True,

            foreground_color = (.4, .4, .4, 1),
            cursor_color = (.4, .4, .4, 1))
        self.newIdea.bind(text=self.on_text)

        self.idea = Label(
            height = self.MINIMUM_HEIGHT,
            size_hint = (None, None),
            pos_hint = {'center_x':.5, 'center_y':.5},
            color = (.4, .4, .4,1))
            

    def add_edge(self, edge):
        self.edges.append(edge)

    def on_text(self, *args):
        self.idea.text = self.newIdea.text
        self.set_size()

    def reset_size(self):
        defaultIdeaWidth = self.originalWidth - self.TEXT_OFFSET

        self.width = self.originalWidth
        self.idea.width = defaultIdeaWidth
        self.newIdea.width = defaultIdeaWidth

    def set_size(self, *args):
        if self.idea.text.strip(): # if there is some text
            ideaWidth = self.idea.texture_size[0]

            # increase the suzes of all components within the vertex, so that they present the whole text at any time
            if ideaWidth > self.originalWidth:
                self.width = ideaWidth + self.TEXT_OFFSET * 2
                self.idea.width = ideaWidth
                self.newIdea.width = ideaWidth + self.TEXT_OFFSET
            else:
                # don't let the vertext get smaller than it's original dize; the user drew it that size so keep it
                self.reset_size()
        else:
            self.reset_size()

    def set_colour(self, colour):
        for i in self.canvas.get_group(None):
            if type(i) is Color:
                i.r, i.g, i.b, i.a = colour

    def select(self):
        self.selected = True
        self.set_colour(self.highlightColour)
        self.remove_widget(self.idea)
        self.add_widget(self.newIdea)
        self.newIdea.readonly = False

        self.deleteButton = DeleteButton(position_hint={'x':0,'center_y':.5}, owner=self)
        self.add_widget(self.deleteButton)

    def deselect(self):
        self.selected = False
        self.set_colour(self.defaultColour)
        self.remove_widget(self.newIdea)
        self.add_widget(self.idea)
        self.newIdea.readonly = True

        if self.deleteButton is not None:
            self.remove_widget(self.deleteButton)
            deleteButton = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                if self.isSelected():
                    self.deselect()
                else:
                    self.select()
            else:
                self.parent.setPressedVertex(self, ButtonPress.TOUCH_DOWN)
                    
        super(Vertex, self).on_touch_down(touch)

    
    def on_touch_move(self, touch):
        if self.isSelected():
            super(Vertex, self).on_touch_move(touch)
            self.notify_edges()
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.parent.setPressedVertex(self, ButtonPress.TOUCH_UP)

        super(Vertex, self).on_touch_up(touch)

    def isSelected(self):
        return self.selected

    def notify_edges(self):
        for i in self.edges:
            i.drawLine()

class ButtonPress(Enum):
    TOUCH_UP = 1
    TOUCH_MOVE = 2
    TOUCH_DOWN = 3
    UNDEFINED = 4

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

class MindMapWidget(FloatLayout):
    firstSelectedVertex = None
    finalSelectedVertex = None

    def __init__(self):
        super(MindMapWidget, self).__init__()

        self.circleShape = [Type.RIGHT_TOP, Type.RIGHT_BOTTOM, Type.LEFT_BOTTOM, Type.LEFT_TOP]
        self.bounds = [None] * 4

    def setPressedVertex(self, vertex, touch):
        if touch == ButtonPress.TOUCH_DOWN:
            self.firstSelectedVertex = vertex
        else:
            if touch == ButtonPress.TOUCH_UP:
                self.finalSelectedVertex = vertex
    
    def getType(self, dx, dy, direction):
        result = Type.UNDEFINED
        
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

        return result

    def getPointsXAndY(self, points, index):
        startIndex = index * 2

        return [points[startIndex], points[startIndex + 1]]

    def isClockwise(self, direction):
        return direction == Direction.CLOCKWISE
            
    def isCircle(self, points, direction): 
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

                    self.bounds[index] = currentPoint
                    
                    # get the latest version of that point, as it will be the extreme of the bounds of the drawn circle
                    if detected.count(newType) == 0:
                        detected[index] = newType
                    else:
                        detected[detected.index(newType)] = newType

                    # because we may start anywhere in the shape, we may need to do circular traversal of the shape array
                    if direction == Direction.CLOCKWISE:
                        index = (index + 1) % len(shape)
                    else:
                        index = (index - 1) % len(shape)

                currentType = newType
                currentPoint = nextPoint

                if shape == detected:
                    result = True
                    break

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

        with self.canvas:
            Color(0, .498, .471) # rgb: 0 ,127, 120
            self.currentLine = Line(points=(touch.x, touch.y))
            touch.ud['line'] = self.currentLine

        super(MindMapWidget, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        touch.ud['line'].points += [touch.x, touch.y]
        super(MindMapWidget, self).on_touch_move(touch)


    def on_touch_up(self, touch):
        super(MindMapWidget, self).on_touch_up(touch)
        direction = None
        try:
            if len(touch.ud['line'].points) > 0:
                points = touch.ud['line'].points

                self.canvas.remove(self.currentLine)
                if self.isCircle(points, self.determineDirection(points)):
                    newIdea = Vertex(pos=(self.bounds[3][0],self.bounds[2][1]), size=(self.bounds[1][0] - self.bounds[3][0], self.bounds[0][1] - self.bounds[2][1]))
                    self.add_widget(newIdea)

                else:
                    if self.firstSelectedVertex is not None and self.finalSelectedVertex is not None: # let's assume this is an edge joining two vertices
                        if self.firstSelectedVertex != self.finalSelectedVertex:
                            newConnection = Edge(vertexOne=self.firstSelectedVertex, vertexTwo=self.finalSelectedVertex)
                            self.add_widget(newConnection) # add it to the start so it's drawn behind everything else

                            self.remove_widget(self.firstSelectedVertex)
                            self.remove_widget(self.finalSelectedVertex)

                            self.add_widget(self.firstSelectedVertex)
                            self.add_widget(self.finalSelectedVertex)

                            self.firstSelectedVertex.add_edge(newConnection)
                            self.finalSelectedVertex.add_edge(newConnection)
                    else:
                        print "unknown"
        except:
            pass

        self.firstSelectedVertex = None
        self.finalSelectedVertex = None


class MindMapApp(App):
    
    def build(self):
        mindmap = MindMapWidget()
        #clearbtn = Button(text='Clear')
        #parent.add_widget(clearbtn)
        
        #def clear_canvas(obj):
            #mindmap.canvas.clear()

        #clearbtn.bind(on_release=clear_canvas)
        
        Config.set('input','multitouchscreen1','tuio,172.19.6.158:3333')
        Config.set('kivy', 'keyboard_mode', 'systemandmulti')
        #Config.set('graphics', 'fullscreen', 'auto')
        return mindmap


if __name__ == '__main__':
    MindMapApp().run()