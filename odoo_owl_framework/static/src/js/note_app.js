/** @odoo-module **/

import { Component, mount, useState } from "@odoo/owl";

class NoteApp extends Component {
    setup() {
        this.state = useState({
            notes: [],
            newTitle: '',
            newContent: '',
        });

        this.loadNotes();
    }

    async loadNotes() {
        const result = await this.rpc("/odoo_owl_todo/api/notes");
        this.state.notes = result;
    }

    async createNote() {
        if (!this.state.newTitle) return;
        const newNote = await this.rpc("/odoo_owl_todo/api/create_note", {
            title: this.state.newTitle,
            content: this.state.newContent,
        });
        this.state.notes.push(newNote);
        this.state.newTitle = '';
        this.state.newContent = '';
    }

    async rpc(route, params = {}) {
        return await fetch(route, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
            },
            body: JSON.stringify(params),
        }).then((response) => response.json())
            .catch((error) => {
                console.error(error);
            })
    }
    static template = `
    <div>
        <div class="mb-3">
            <input type="text" t-model="state.newTitle" placeholder="Title" class="form-control mb-2"/>
            <textarea t-model="state.newContent" placeholder="Content" class="form-control mb-2"/>
            <button class="btn btn-primary" t-on-click="createNote">Add Note</button>
        </div>
        <ul class="list-group">
            <li t-foreach="state.notes" t-as="note" class="list-group-item">
                <strong><t t-esc="note.name"/></strong><br/>
                <span><t t-esc="note.content"/></span>
            </li>
        </ul>
    </div>`;
}

    document.addEventListener("DOMContentLoaded", () => {
        const el = document.querySelector("#note-app-root");
        if (el) {
            mount(NoteApp, {target: el});
        }
    });