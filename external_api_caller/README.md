# Custom API Caller

This Odoo module provides an abstract mixin model that allows any model to easily call external APIs using a shared method.

## 📦 Module Name

`external_api_caller`

## 🧩 Features

- Abstract reusable mixin (`api.abstract.mixin`)
- Easily call external APIs with a standard method
- Automatically includes Bearer Token authorization
- Logs request/response info and handles common errors
- Designed for easy inheritance by any model

## 🧱 Installation

1. Copy this module into your custom addons directory.
2. Restart your Odoo server.
3. Install the module via Apps.

## ⚙️ Configuration

Set your Bearer Token in **System Parameters**:

- **Key**: `external_api_caller.bearer_token`
- **Value**: `your_api_token_here`

You can find this in:
`Settings → Technical → Parameters → System Parameters`

## 🧬 How to Use

To make a model use the API caller, simply inherit from the mixin:

```python
class ResPartner(models.Model):
    _inherit = ['res.partner', 'api.abstract.mixin']
```

Then you can directly call:

```python
response = self.call_external_api(
    url="https://api.example.com/data",
    method="GET"
)
```

## 🔧 Method Reference

### `call_external_api(...)`

**Parameters:**

| Name             | Type   | Description                               |
| ---------------- | ------ | ----------------------------------------- |
| `url`            | `str`  | Full URL to call                          |
| `method`         | `str`  | HTTP method: GET, POST, PUT, DELETE       |
| `payload`        | `dict` | JSON-serializable body payload (optional) |
| `custom_headers` | `dict` | Additional headers (optional)             |
| `timeout`        | `int`  | Timeout in seconds (default: 10)          |

**Returns:**

- JSON-decoded response as a `dict`
- Or a dict containing `error` if request failed

## 📄 License

This module is provided under the [Odoo Proprietary License (OPL-1)](https://www.odoo.com/documentation/user/16.0/legal/licenses/licenses.html).

---

**Developed by:**  
Agung Sepruloh
