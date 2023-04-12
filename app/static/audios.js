Vue.component("modal", {
  template: "#modal-template"
});
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
      allUsersData: null,
      editModal: false,
      updatedAudioName: "",
      currentDisplay: "",
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
            this.currentDisplay = "libraryScreen";
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
        console.log(this.updatedAudioName);
        if (this.updatedAudioName != "") {
          axios
          .put(this.serviceURL+"/users/" + this.loggedIn + "/audios/" + audioID, {
              "audioName": this.updatedAudioName
          })
          .then(response => {
              if (response.data.status == "success") {
                this.updatedAudioName = "";
                
                this.hideModal();
                alert("Audio Updated Successfully");
                this.fetchUserAudioLib();
              }
          })
          .catch(e => {
              alert("New audio name should not be the same as current audio name. Please try again");
              console.log(e);
          });
        } else {
          alert("audio name field can't be blank");
        }
      },

      deleteAudio(audioID) {
        axios
        .delete(this.serviceURL+"/users/" + this.loggedIn + "/audios/" + audioID)
        .then(response => {
          console.log(response.data.status);
            alert("Audio deleted Successfully");
            this.fetchUserAudioLib();
        })
        .catch(e => {
          console.log(e);
          alert("Unable to delete the audio");
        });
      },

      getUsers(){
        axios
        .get(this.serviceURL+"/users")
        .then(response => {
          if (response.data.status == "success") {
              this.allUsersData = response.data.users;
              this.currentDisplay = "searchUserScreen";
            }
        })
        .catch(e=>{
          console.log(e);
          alert("unable to display users");
        });
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
