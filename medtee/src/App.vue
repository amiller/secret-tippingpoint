<template>
  <div>
  <div class="container">
      <div class="level-item has-text-centered">
        <h1 class="title">medTEE</h1>
      </div>
      <hr>
      <br>
      <div class="level-item has-text-centered">
      <div>
          <p class="heading">Is connected?  </p>
          <p class="title">{{isConnected ? "Yes" : "No"}}</p>
      </div>
      </div>
      <br>
      <div class="level-item has-text-centered">

        <button rounded class="button is-medium is-info is-light"
          @click="connect"
          :disabled="isConnected">
          Bootstrap
        </button>
      </div>
      <br>

      <hr>
      <nav class="level is-mobile" v-for="item in items">
          <div class="level-item has-text-centered">
          <div>
            <p class="heading">Batch ID:</p>
            <p class="title"> {{item.batchid}}</p>

          </div>
          </div>
          <div class="level-item has-text-centered">
          <div>
            <p class="heading">Name:</p>
            <p class="title"> {{item.name}}</p>
          </div>
          </div>
          <div class="level-item has-text-centered">
          <div>
            <p class="heading">Threshold reached?: </p>
            <p class="title"> {{item.threshold_reached}}</p>
          </div>
          </div>
          <div class="level-item has-text-centered">
          <div>
            <p class="heading">locations:  </p>
            <p class="title">{{item.locations}}</p>
          </div>
        </div>
      
      </nav>
      <!-- <button @click="incrementCount">{{loading ? 'Loading...' : 'Increment by 1'}}</button> -->
      <hr>
      <div class="buttons level-item has-text-centered">
        <!-- <button rounded class="button is-medium is-primary is-light" @click="createBatch">{{loading ? 'creating...' : 'Create default batch'}}</button> -->
        <!-- <button rounded class="button is-medium is-primary is-light" @click="addPatient">{{loading ? 'adding...' : 'Add patient'}}</button> -->
        <button rounded class="button is-medium is-success is-light" @click="getCount">Sanity test</button>
        <button rounded class="button is-medium is-success is-light" @click="checkBatches">Check all batches</button>
      </div>

      <hr>
      <div class="inputs level-item has-text-centered">
              <input class="input is-primary is-medium" v-model="name" placeholder="Drug name" />
        <input class="input is-primary is-medium" v-model="batchid" placeholder="Batch id" />
        <input class="input is-primary is-medium" v-model="token" placeholder="User token given by pharmacy" />

      </div>
      <br>


      <div class="buttons level-item has-text-centered">
        <button rounded class="button is-medium is-info is-light" @click="addBatch">{{loading ? 'loading...' : 'Track a new batch'}}</button>
        <button rounded class="button is-medium is-info is-light" @click="addSymptom">{{loading ? 'loading...' : 'Mark symptom'}}</button>
      </div>
    </div>


    <hr>
      <div class="level-item has-text-centered">
      <div>
        <p class="heading">Sanity test: {{count}}</p>
      </div>
      </div>
  </div>
</template>

<script>
import { counterContract } from './contracts/counter';
import { bootstrap, onAccountAvailable } from '@stakeordie/griptape.js';

export default {


  data: () => ({
    count: '',
    items: [{
      batchid: 42,
      name: "Blue pill",
      token: 42,
      locations: [],
      threshold_reached: false
    }],
    loading: false,
    isConnected: false,
    removeOnAccountAvailable:null
  }),
  mounted(){
    this.removeOnAccountAvailable = onAccountAvailable(()=>{
      this.isConnected= true;
    })

    this.checkBatches();
  },
  unmounted(){
    this.removeOnAccountAvailable()
  },
  methods: {
    async checkBatches() {

      for (var item of this.items) {
        console.log("checking batch ...");
        console.log(item);
        const response = await counterContract.checkBatch(item.batchid);
        console.log("got response: ", response);
        item.locations = response.locations;
        console.log("this.locations: ", this.locations);
        item.threshold_reached = response.threshold_reached;
        console.log("this.threshold_reached: ", this.threshold_reached);
      }
    },
    async getCount() {
      const response = await counterContract.getCount();
      
      this.count = response.count;
      this.loading = false;
    },
    async connect() {
      await bootstrap();
    },

    async createBatch() {
      this.loading = true;
      await counterContract.createBatch();
      this.loading = false;
    },


    async addBatch() {
      this.loading = true;
      var batchid = parseInt(this.batchid);
      var name = this.name;
      var token = parseInt(this.token);
      this.loading = false;
      console.log(batchid)
      this.items.push({
        batchid: batchid,
        name: name,
        token: token,
        locations: [],
        threshold_reached: false
      })
    },

    async addSymptom() {
      var batchid = parseInt(this.batchid);
      this.loading = true;

      var name = "";
      var token = 0;
      for (var item of this.items) {
        if (item.batchid == batchid) {
          name = item.name;
          token = item.token;
          break;
        }
      }
      console.log(batchid, token)
      await counterContract.addSymptom(batchid, token)
      this.loading = false;
    },

    //async addPatient() {
    //  this.loading = true;
    //  await counterContract.addPatient();
    //  this.loading = false;
    //}
    async addPatient() {
      this.loading = true;
      setTimeout(async () => {
        await counterContract.addPatient();
        this.loading = false;
      }, 100);
    }
    //async incrementCount() {
    //  this.loading = true;
    //  await counterContract.incrementCount();
    //  this.loading = false;
    //}
  }
}
</script>
