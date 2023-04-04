var app = new Vue({
    el: "#app",
  
    //------- data --------
    data: {
      serviceURL: "https://cs3103.cs.unb.ca:50619",
      authenticated: false,
      loggedIn: null,
      libraryData: null,
      audioData: null,
      userData: null,
      editModal: false,
      input: {
        username: "",
        password: ""
      },
      selectedAudio: {
        audioFile: "",
        audioID: "",
        audioName: "",
        userID: ""
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
                this.getCurrentUser();
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
      getCurrentUser(){
        axios
        .get(this.serviceURL+"/users/" + this.loggedIn)
        .then(response => {
          this.userData = response.data.user;
        })
        .catch(e => {
          alert("Unable to load the requested user");
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
      },

      selectAudio(audioID) {
        this.showModal();
        for (x in this.libraryData) {
          if (this.libraryData[x].audioID == audioID) {
            this.selectedAudio = this.libraryData[x];
          }
        }
        console.log(this.selectedAudio);
      },

      updateAudio(audioID) {
        if (this.selectedAudio.audioName != "") {
          axios
          .update(this.serviceURL+"/users/" + this.loggedIn + "/audios/" + audioID, {
              "audioName": this.selectedAudio.audioName
          })
          .then(response => {
              if (response.data.status == "success") {
                this.selectedAudio.audioName = "";
                
                this.hideModal();
                alert("Audio Updated Successfully");
              }
          })
          .catch(e => {
              alert("Unable to update, please try again");
              console.log(e);
          });
        } else {
          alert("put audio name");
        }
      },

      deleteAudio(audioID) {
        axios
        .delete(this.serviceURL+"/users/" + this.loggedIn + "/audios/" + audioID)
        .catch(e => {
          alert("Unable to delete the audio");
          console.log(e);
        });
        location.reload();
      },

      showModal() {
        this.editModal = true;
      },
  

      hideModal() {
        this.editModal = false;
      }
  
  
    }
    //------- END methods --------
  
  });
