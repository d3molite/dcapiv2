axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

data = JSON.parse(document.getElementById('cogData').textContent)

var vue_data = {
    "cog": data,
    "editName": false,
}


app = Vue.createApp({
    delimiters: ["[[", "]]"],
    data() {
        return vue_data
    },
    mounted() {
        console.log("Vue Mounted.")
    },
    methods: {
        deleteDataPoint(data) {

            console.log(data)

            // iterate over all cogs data
            for (i = 0; i < this.cog.data.length; i++) {
                var c = this.cog.data[i]

                var del = true

                // iterate over the cog subdata
                for (j = 0; j < c.length; j++) {
                    var d = c[j]
                    var cd = data[j]

                    if (d.data != cd.data) {
                        del = false
                    }
                }

                if (del) {
                    this.cog.data.splice(i, 1)
                }
            }
        },
        addDataPoint() {
            var temp = JSON.parse(JSON.stringify(this.cog.template))
            this.cog.data.push(temp)
        },
        save() {
            axios({
                method: "post",
                url: window.location.href + "save/",
                data: this.cog
            })
        },
        prettify_key(value) {
            split = value.split("_")
            ret = ""
            for (i = 0; i < split.length; i++) {
                split[i] = split[i].charAt(0).toUpperCase() + split[i].slice(1)
            }
            return split.join(" ")
        },
    }
}).mount("#app")