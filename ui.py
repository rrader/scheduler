from tkinter import *
from tkinter import simpledialog
from graph import new_node

CONNECT, DRAW = range(2)


class UI():
    def __init__(self):
        self.root = Tk()
        self.canvas = None
        self.nodes = {}
        self.connections = {}
        self.selected = None
        self.move = False
        self.id = 0
        self.start_x = 0
        self.start_y = 0
        self.state = DRAW
        self.current_line = None
        self.connection = False

    def connect_command(self):
        text = self.canvas.find_withtag("action")
        self.canvas.itemconfig(text, text="connection")
        self.state = CONNECT

    def draw_command(self):
        text = self.canvas.find_withtag("action")
        self.canvas.itemconfig(text, text="drawing")
        self.state = DRAW

    def build(self):
        top = Frame(self.root)
        bottom = Frame(self.root)
        top.pack(side=TOP)
        bottom.pack(side=BOTTOM, fill=BOTH, expand=True)

        b = Button(self.root, text="Connect", width=4, height=1, command=self.connect_command)
        c = Button(self.root, text="Draw", width=4, height=1, command=self.draw_command)
        b.pack(in_=top, side=LEFT)
        c.pack(in_=top, side=LEFT)

        self.canvas = Canvas(self.root, width=800, height=600, bg='white')
        self.canvas.bind("<Double-Button-1>", self.add_node)
        self.canvas.pack(in_=bottom, expand=YES, fill=BOTH)
        self.canvas.create_text(50, 10, text="drawing", tags="action")

    def show(self):
        self.build()
        self.root.mainloop()

    def add_node(self, event):
        if self.state == DRAW:
            i = self.draw_circle(event.x, event.y, 20)
            self.nodes[i] = new_node()
            if not self.selected:
                self.selected = i
            self.redraw()

    def get_node_at_coord(self, x, y):
        q = self.canvas.find_closest(x, y)
        print(self.canvas.gettags(q))
        if "node" in self.canvas.gettags(q):
            return int(list(filter(None, re.findall("\d*", self.canvas.gettags(q)[0])))[0])

    def get_line_at_coord(self, x, y):
        q = self.canvas.find_closest(x, y)
        print(self.canvas.gettags(q))
        if "line" in self.canvas.gettags(q):
            return [int(x) for x in list(filter(None, re.findall("\d*", self.canvas.gettags(q)[0])))]
        return None, None

    def node_selected(self, event):
        self.selected = self.get_node_at_coord(event.x, event.y)
        print("selected ", self.selected)
        self.redraw()

    def node_start_move(self, event):
        self.selected = self.get_node_at_coord(event.x, event.y)
        print("selected ", self.selected)
        self.redraw()
        if self.state == DRAW:
            self.move = True
            self.start_x = event.x
            self.start_y = event.y

        if self.state == CONNECT:
            self.connection = True
            self.source = self.selected

    def node_move(self, event):
        if self.move:
            items = self.node_elements(self.selected)
            for i in items:
                q = self.canvas.coords(i)
                self.canvas.move(i, ((event.x - self.start_x)),
                                    ((event.y - self.start_y)))
            self.start_x = event.x
            self.start_y = event.y
            self.redraw()

    def node_stop_move(self, event):
        if self.state == DRAW:
            self.move = False
        if self.state == CONNECT:
            self.connection = False
            self.selected = self.get_node_at_coord(event.x, event.y)
            self.redraw()
            if self.source and self.selected and self.source != self.selected:
                self.connections[(self.source, self.selected, )] = 1
                self.draw_line(self.source, self.selected)

    def node_modify(self, event):
        i = self.get_node_at_coord(event.x, event.y)
        if not i:
            return
        weight = simpledialog.askinteger("Weight", "Enter weight of node {}".format(i),
                                         initialvalue=self.nodes[i]['weight'])
        if weight:
            self.nodes[i]['weight'] = weight
        self.redraw()

    def line_modify(self, event):
        start, end = self.get_line_at_coord(event.x, event.y)
        if not start:
            return
        weight = simpledialog.askinteger("Weight", "Enter weight of connection {}-{}".format(start, end),
                                         initialvalue=self.connections[(start, end)])
        if weight:
            self.connections[(start, end)] = weight
        self.redraw()

    def draw_circle(self, x, y, rad):
        self.id += 1
        tag = "item{}".format(self.id)
        oval = self.canvas.create_oval(x-rad, y-rad, x+rad, y+rad, width=2, fill='white', tags=(tag, tag+"o", "node"))
        name = self.canvas.create_text(x, y-rad/2, text=str(self.id), tags=(tag, tag+"n", "node"))
        line = self.canvas.create_line(x-rad, y, x+rad, y, width=2, fill='black', tags=(tag, tag+"l", "node"))
        weight = self.canvas.create_text(x, y+rad/2, text="", tags=(tag, tag+"w", "node"))
        self.canvas.tag_bind(tag, "<Button-3>", self.node_modify)
        self.canvas.tag_bind(tag, "<ButtonPress-1>", self.node_start_move)
        self.canvas.tag_bind(tag, "<B1-Motion>", self.node_move)
        self.canvas.tag_bind(tag, "<ButtonRelease-1>", self.node_stop_move)
        return self.id

    def draw_line(self, start, stop):
        tag = "line{}_{}".format(start, stop)
        s = self.canvas.coords(self.node_elements(start)[0])
        e = self.canvas.coords(self.node_elements(stop)[0])
        line_lbl = self.canvas.create_text((s[0]+e[0])/2, (s[1]+e[3])/2,
                                           text=str(self.connections[(start, stop)]), tags=(tag, tag+"t", "line"))
        line = self.canvas.create_line((s[0]+s[2])/2, (s[1]+s[3])/2, (e[0]+e[2])/2, (e[1]+e[3])/2,
                                       width=1, fill='black', arrow="last", tags=(tag, tag+"l", "line"))
        self.canvas.tag_bind(tag, "<Button-3>", self.line_modify)
        self.canvas.tag_raise(line)
        return self.id

    def redraw(self):
        for i in self.nodes.keys():
            self.configure_node(i)

        for s_n, e_n in self.connections.keys():
            ltag = "line{}_{}".format(s_n, e_n)
            c = self.canvas.coords(ltag + "l")
            self.canvas.itemconfig(ltag + "t", text=str(self.connections[(s_n, e_n)]))
            o1, o2 = self.node_elements(s_n)[0], self.node_elements(e_n)[0]
            s = self.canvas.coords(o1)
            e = self.canvas.coords(o2)
            self.canvas.coords(ltag + "l", (s[0]+s[2])/2, (s[1]+s[3])/2, (e[0]+e[2])/2, (e[1]+e[3])/2)
            self.canvas.coords(ltag + "t", (s[0]+e[0])/2, (s[1]+e[3])/2)

    def configure_node(self, i):
        oval, name, line, weight = self.node_elements(i)
        node = self.nodes[i]
        if self.selected == i:
            self.canvas.itemconfig(oval, outline="blue")
        else:
            self.canvas.itemconfig(oval, outline="black")
        self.canvas.itemconfig(weight, text=str(node['weight']))

    def node_elements(self, n_id):
        tag = "item{}".format(n_id)
        oval = self.canvas.find_withtag(tag + "o")
        name = self.canvas.find_withtag(tag + "n")
        line = self.canvas.find_withtag(tag + "l")
        weight = self.canvas.find_withtag(tag + "w")
        return oval, name, line, weight
