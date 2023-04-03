var app = new Vue({
    el: "#app",
  
    //------- data --------
    data: {
      serviceURL: "https://cs3103.cs.unb.ca:50619",
      authenticated: false,
      loggedIn: null,
      libraryData: null,
      input: {
        username: "",
        password: ""
      }
    },
    methods: {
      login() {
        if (this.input.username != "" && this.input.password != "") {
          axios
          .post(this.serviceURL+"/signin", {
              "username": this.input.username,
              "password": this.input.password
          })
          .then(response => {
              if (response.data.status == "success") {
                this.authenticated = true;
                this.loggedIn = response.data.user_id;
                console.log(this.loggedIn);
              }
          })
          .catch(e => {
              alert("The username or password was incorrect, try again");
              this.input.password = "";
              console.log(e);
          });
        } else {
          alert("A username and password must be present sss");
        }
      },
  
  
      logout() {
        axios
        .delete(this.serviceURL+"/signin")
        .then(response => {
            if (response.data.status == "success") {
                this.authenticated = false;
                this.loggedIn = NULL
              }
            location.reload();
        })
        .catch(e => {
            alert("user is not logged in");
            console.log(e);
        });


        
      },
  
      fetchUserAudioLib() {
        axios
        .get(this.serviceURL+"/users/" + this.loggedIn + "/audios")
        .then(response => {
            this.libraryData = response.data.library;
        })
        .catch(e => {
          alert("Unable to load the audio library");
          console.log(e);
        });
      }
  
  
    }
    //------- END methods --------
  
  });