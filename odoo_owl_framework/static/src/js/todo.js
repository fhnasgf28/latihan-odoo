/** @odoo-module **/

import { Component, mount } from "@odoo/owl";
import { jsonrpc } from "@web/core/network/rpc_service";

class TodoApp extends Component {
    static template = "odoo_owl_framework.TodoComponent";

    setup() {
        this.state = {
            tasks: [],
            newTask: "",
        };
        this.loadTasks();
    }

    async loadTasks() {
        const result = await jsonrpc("/odoo_owl_todo/get_tasks", {});
        this.state.tasks = result.tasks;
    }

    async addTask() {
        if (!this.state.newTask.trim()) return;
        const newText = this.state.newTask.trim();
        await jsonrpc("/odoo_owl_todo/add_task", { text: newText });
        this.state.tasks.push({ id: Date.now(), text: newText });
        this.state.newTask = "";
    }

    onInput(ev) {
        this.state.newTask = ev.target.value;
    }
}

mount(TodoApp, document.getElementById("todo-app-root"));
