
var app = new Vue({
    el: "#app",
  
    //------- data --------
    data: {
      serviceURL: "https://cs3103.cs.unb.ca:8024",
      authenticated: false,
      loggedIn: null,
      libraryData: null,
      audioData: null,
      allUsersData: null,
      editModal: false,
      updatedAudioName: "",
      currentDisplay: "",
      userData: null,
      modalAdd: false,
      input: {
        username: "",
        password: ""
      },
      audioForm: {
        audioName: "",
        audioFile: null
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
      getUserAudioLibrary() {
        const username = document.getElementById("username").value;
        axios.get(`/users/${username}`)
        .then(response => {
            const UserId = response.data.Users.userID;
            axios.get(`${this.serviceURL}/users/${UserId}/audios`)
            .then(response => {
              this.libraryData = response.data.library;
            })
            .catch(e => {
              alert("Unable to load the audio library");
              console.log(e);
            });
        })
        .catch(e => {
          alert("Unable to load the user");
          console.log(e);
        });
      }
      ,
      addAudio(){
        let fileInput = document.getElementById('audioFile');
        let selectedFile = fileInput.files[0];
        let fileName = selectedFile.name;
        const audioFile = document.getElementById('audioFile').files[0];
        const audioName = document.getElementById('audioName').value;
        const formData = new FormData();
        formData.append('file', audioFile);
        formData.append('audioName', audioName);
        if (this.audioForm.audioName !== "" && this.audioForm.audioFile.size !== null) {
          axios
          .post(this.serviceURL + "/users/" + this.loggedIn + "/audios", {
            "audioName": this.audioForm.audioName,
            "audioFile": fileName
          })
          .catch(e => {
            alert("unable to add the audio file");
            console.log(e);
          })
          axios.post('/FileUpload', formData)
          .then(response => {
            if (response.data.status === 'success') {
              this.modalAdd=false;
              alert('Audio added successfully');
            }
          })
          .catch(error => {
            console.error(error);
            alert('Unable to add audio');
          });
        }
      },
      selectAudio(audioID) {
        this.showEditModal();
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
                
                this.hideEditModal();
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

      showModalAdd() {
        this.modalAdd = true;
      },

      hideModal(){
        this.modalAdd = false;
      },

      showEditModal() {
        this.editModal = true;
      },

      hideEditModal() {
        this.editModal = false;
      }
  
  
    }
    //------- END methods --------
  
  });
