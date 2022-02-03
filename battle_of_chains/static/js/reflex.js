import { Application } from 'stimulus'
import StimulusReflex from 'stimulus_reflex'
import WebsocketConsumer from 'sockpuppet-js'
import Controller from './controller'

const application = Application.start()
const ssl = location.protocol !== 'https:' ? '' : 's';
const consumer = new WebsocketConsumer(`ws${ssl}://${location.hostname}:${location.port}/ws/sockpuppet-sync`)


application.register("controller", Controller)
StimulusReflex.initialize(application, { consumer })
