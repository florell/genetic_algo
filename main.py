import random
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd
import matplotlib.pyplot as plt

FUNCTIONS = ["4*(x-5)**2+(y-6)**2"]


def evaluate_function(x, y):
    return eval(FUNCTIONS[0])


def generate_initial_population(size, start, end):
    population = []
    for _ in range(size):
        x = random.uniform(start, end)
        y = random.uniform(start, end)
        individual = [x, y, evaluate_function(x, y)]
        population.append(individual)
    return population


def crossover(parent1, parent2):
    child1 = [parent1[0], parent2[1], evaluate_function(parent1[0], parent2[1])]
    child2 = [parent2[0], parent1[1], evaluate_function(parent2[0], parent1[1])]
    return child1, child2


def mutate(child):
    x, y = child[0], child[1]
    if random.random() > 0.5:
        x += random.uniform(-0.5, 0.5)
    else:
        y += random.uniform(-0.5, 0.5)
    return [x, y, evaluate_function(x, y)]


def genetic_algorithm(num_generations, population_size, start, end):
    data_for_table = []
    snapshot_arr = []
    
    population = generate_initial_population(population_size, start, end)

    for i in range(num_generations):
        for _ in range(population_size):
            parent1 = random.choice(population)
            parent2 = random.choice(population)
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1)
            child2 = mutate(child2)
            population.append(child1)
            population.append(child2)

        population = sorted(population, key=lambda ind: ind[2])
        population = population[:population_size]
        data_for_table.append(population[0])

        x = [ind[0] for ind in population]
        y = [ind[1] for ind in population]
        snapshot_name = f"pictures/g{i}.png"
        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.suptitle(f"Generation Number: {i}")
        ax2.set_xlabel("Function Values")
        ax2.plot(x, y, 'mo')
        ax2.set_xlim(start, end)
        ax2.set_ylim(start, end)
        ax1.set_xlabel("Function Values Zoomed In")
        ax1.plot(x, y, 'mo')
        plt.savefig(snapshot_name, dpi=70, bbox_inches='tight')
        plt.close()
        snapshot_arr.append(snapshot_name)

    data = pd.DataFrame(data_for_table)
    data.columns = ['X', 'Y', 'Minimum F(x,y)']

    return population[0], data


class ShowResult:
    def __init__(self, data):
        self.i = 0
        self.max_i = int(num_generations_var.item.get()) - 1
        self.canvas = Canvas(frame_btn, width=420, height=345, borderwidth=2)
        self.photo = None
        self.show_img()

        self.button_next = ttk.Button(frame_btn, text="Next", command=self.next_img, state=NORMAL)
        self.button_next.grid(row=1, column=1)
        self.button_back = ttk.Button(frame_btn, text="Back", command=self.previous_img, state=DISABLED)
        self.button_back.grid(row=1, column=0)

        self.data = data
        self.show_table()

    def next_img(self):
        self.i += 1
        self.button_back['state'] = NORMAL
        self.show_img()
        if self.i == self.max_i:
            self.button_next['state'] = DISABLED

    def previous_img(self):
        self.i -= 1
        self.button_next['state'] = NORMAL
        self.show_img()
        if self.i == 0:
            self.button_back['state'] = DISABLED

    def show_img(self):
        self.photo = ImageTk.PhotoImage(Image.open(f"pictures/g{self.i}.png"))
        self.canvas.create_image(3, 3, anchor='nw', image=self.photo)
        self.canvas.grid(column=0, row=0, columnspan=2)

    def show_table(self):
        treeview = ttk.Treeview(frame_scroll, columns=list(self.data.columns), show='headings')
        treeview.pack(side=LEFT, fill=BOTH, expand=1)

        for col in self.data.columns:
            treeview.heading(col, text=col)

        for _, row in self.data.iterrows():
            treeview.insert('', END, values=list(row))

        scrollbar = ttk.Scrollbar(frame_scroll, orient=VERTICAL, command=treeview.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        treeview.configure(yscrollcommand=scrollbar.set)


def check_button_state(*args):
    if (num_generations_var.item.get() and population_size_var.item.get() and start_var.item.get() and
            end_var.item.get() and combobox_var.get()):
        btn_start['state'] = NORMAL
    else:
        btn_start['state'] = DISABLED
    if (num_generations_var.item.get() or population_size_var.item.get() or start_var.item.get() or
            end_var.item.get() or combobox_var.get()):
        btn_clean['state'] = NORMAL



def click_button():
    btn_start['state'] = DISABLED
    xy_best_score, data = genetic_algorithm(
        population_size=int(population_size_var.item.get()),
        num_generations=int(num_generations_var.item.get()),
        start=min(int(start_var.item.get()), int(end_var.item.get())),
        end=max(int(start_var.item.get()), int(end_var.item.get()))
    )

    for widget in frame_input.winfo_children():
        if widget.winfo_name() == "result_label":
            widget.destroy()
    for widget in frame_btn.winfo_children():
        widget.destroy()
    for widget in frame_scroll.winfo_children():
        widget.destroy()

    ShowResult(data)
    text = "x={0} y={1}; \n Minimum F(x,y): {2}".format(xy_best_score[0], xy_best_score[1], xy_best_score[2])
    Label(frame_input, text=text, fg='red', font=('Arial', 10), name="result_label").pack()


def clean_button():
    population_size_var.item.delete(0, END)
    num_generations_var.item.delete(0, END)
    start_var.item.delete(0, END)
    end_var.item.delete(0, END)
    combobox_var.set('')
    for widget in frame_input.winfo_children():
        if widget.winfo_name() == "result_label":
            widget.destroy()
    for widget in frame_btn.winfo_children():
        widget.destroy()
    for widget in frame_scroll.winfo_children():
        widget.destroy()


class UserInput:
    def __init__(self, text, from_, to, increment, initial_value):
        self.var = StringVar()
        self.var.set(initial_value)

        Label(frame_input, text=text).pack()
        self.item = ttk.Spinbox(frame_input, validate='key', textvariable=self.var,
                                from_=from_, to=to, increment=increment)
        self.item.pack()
        self.var.trace('w', check_button_state)


root_window = Tk()
root_window.title("Genetic Algorithm")
root_window.geometry('1200x700')

style = ttk.Style(root_window)
style.theme_use('clam')

frame_input = Frame(root_window, bd=3, relief=GROOVE)
frame_input.grid(column=0, row=0, rowspan=2, sticky='NSEW')

frame_img = LabelFrame(root_window, bd=3, relief=GROOVE, text="Graphs")
frame_img.grid(column=1, row=0, sticky='NSEW')

frame_table = LabelFrame(root_window, bd=3, relief=GROOVE, text="Table")
frame_table.grid(column=1, row=1, sticky='NSEW')

frame_btn = Frame(frame_img)
frame_btn.pack(fill=BOTH, expand=1)

frame_scroll = Frame(frame_table)
frame_scroll.pack(fill=BOTH, expand=1)

root_window.columnconfigure(0, weight=1)
root_window.columnconfigure(1, weight=4)
root_window.rowconfigure(0, weight=1)
root_window.rowconfigure(1, weight=1)

font_style = ('Arial', 12)

Label(frame_input, text="Target Function:", font=font_style).pack()
var_txt = StringVar()
combobox_var = ttk.Combobox(frame_input, textvariable=var_txt, font=font_style)
combobox_var['values'] = FUNCTIONS
combobox_var['state'] = 'readonly'
combobox_var.pack(padx=5, pady=5)
var_txt.trace('w', check_button_state)

population_size_var = UserInput(text="Population Size:", initial_value="10", from_=2, to=999, increment=1)
num_generations_var = UserInput(text="Number of Generations:", initial_value="10", from_=1, to=999, increment=1)
start_var = UserInput(text="Lower Search Range:", initial_value="-10", from_=-99999, to=99999, increment=1)
end_var = UserInput(text="Upper Search Range:", initial_value="10", from_=-99999, to=99999, increment=1)

btn_start = ttk.Button(frame_input, text="Calculate", command=click_button, state=DISABLED, style='TButton')
btn_start.pack(padx=5, pady=5)

btn_clean = ttk.Button(frame_input, text="Clear", command=clean_button, state=DISABLED, style='TButton')
btn_clean.pack(padx=5, pady=5)

root_window.mainloop()
