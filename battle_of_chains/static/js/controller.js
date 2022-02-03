import { Controller } from 'stimulus';
import StimulusReflex from 'stimulus_reflex';


export default class extends Controller {
  connect() {
    StimulusReflex.register(this)
  }

  filter(event) {
    event.preventDefault()
    this.stimulate('MarketReflex#filter', event.target)
  }

  clear_filters(event) {
    event.preventDefault()
    this.stimulate('MarketReflex#clear_filters', event.target)
  }

  sort(event) {
    event.preventDefault()
    this.stimulate('MarketReflex#sort', event.target)
  }

  page(event) {
    event.preventDefault()
    this.stimulate('MarketReflex#page', event.target)
  }

}
