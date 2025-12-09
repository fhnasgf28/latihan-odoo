/** @odoo-module **/

import { Component, useState, useRef } from "@odoo/owl";
import { TodoItem } from "../todo_item/todo_item";

export class TodoApp extends Component {
    // Definisi template untuk komponen ini
    static template = "odoo_owl_framework.TodoApp";

    // Mendaftarkan sub-komponen yang digunakan di dalam template ini
    static components = { TodoItem };

    setup() {
        // Menggunakan useState untuk membuat state reaktif
        this.state = useState({
            todos: [], // Array untuk menyimpan daftar tugas
            nextId: 1, // ID unik untuk tugas berikutnya
        });

        // Menggunakan useRef untuk mendapatkan referensi ke input elemen HTML
        this.taskInput = useRef("taskInput");

        // Contoh inisialisasi dengan beberapa tugas dummy
        this.state.todos = [
            { id: this.state.nextId++, description: "Learn Odoo OWL", isCompleted: false },
            { id: this.state.nextId++, description: "Build a cool app", isCompleted: true },
        ];
    }

    addTask() {
        const description = this.taskInput.el.value.trim();
        if (description) {
            this.state.todos.push({
                id: this.state.nextId++,
                description: description,
                isCompleted: false,
            });
            this.taskInput.el.value = ""; // Bersihkan input
        }
    }

    onTaskInputKeyup(ev) {
        // Jika tombol Enter ditekan
        if (ev.key === "Enter") {
            this.addTask();
        }
    }

    toggleTodoCompleted(ev) {
        // Event ini dipancarkan dari TodoItem, membawa 'id' tugas
        const todo = this.state.todos.find(t => t.id === ev.detail.id);
        if (todo) {
            todo.isCompleted = !todo.isCompleted;
        }
    }

    deleteTodo(ev) {
        // Event ini dipancarkan dari TodoItem, membawa 'id' tugas
        this.state.todos = this.state.todos.filter(t => t.id !== ev.detail.id);
    }
}