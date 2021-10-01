data = JSON.parse(document.getElementById('botsData').textContent)

var vue_data = { "bots": [] }

app = Vue.createApp({
    delimiters: ["[[", "]]"],
    data() {
        return vue_data
    },
    mounted() {
        setInterval(function () {
            i = 0
            if (data.length > 0) {
                item = data.pop(i)
                app.bots.push(item)
                i++
            }
        }, 250)
        clearInterval()

    },
}).mount("#app")