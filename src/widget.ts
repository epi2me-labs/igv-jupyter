import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers,
} from '@jupyter-widgets/base';

import igv from 'igv';

import { MODULE_NAME, MODULE_VERSION } from './version';

if (!igv.browserCache) {
  igv.browserCache = {}
}

interface ICustomMessage {
  type: string,
  [x: string]: any
}

interface IBrowserTrack {
  name: string,
  url: string,
  [x: string]: any
}

interface IBrowserGenome {
  id: string,
  name: string,
  fastaURL: string,
  indexed: boolean,
  indexURL?: string,
  aliasURL?: string,
  cytobandURL?: string,
  tracks?: IBrowserTrack[]
}

interface IBrowserOptions {
  id: string,
  tracks: IBrowserTrack[],
  locus: string,
}

interface IBrowserOptionsGenome extends IBrowserOptions {
  genome: string,
  reference?: never,
}

interface IBrowserOptionsReference extends IBrowserOptions {
  genome?: never,
  reference: IBrowserGenome,
}

export class IGVModel extends DOMWidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: IGVModel.model_name,
      _model_module: IGVModel.model_module,
      _model_module_version: IGVModel.model_module_version,
      _view_name: IGVModel.view_name,
      _view_module: IGVModel.view_module,
      _view_module_version: IGVModel.view_module_version,
    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
  };

  static model_name = 'IGVModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'IGVMainView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;
}

export class IGVMainView extends DOMWidgetView {
  public options: IBrowserOptionsGenome | IBrowserOptionsReference;

  render() {
    // Load initial config to hydrate browser
    this.options = this.model.get('initialConfig')

    // Create the IGV.js browser in this view
    this.createBrowser(this.el)

    // Handle updating managed state
    this.model.on('change:locus', this.locus_changed, this);

    // Handle RPC-like method calls from the backend
    this.model.on("msg:custom", this.handle_custom_messages, this);
    this.model.on("removeTrack", this.removeTrack, this);
    this.model.on("loadTrack", this.loadTrack, this);
    this.model.on("loadGenome", this.loadGenome, this);
    this.model.on("remove", this.removeBrowser, this);
    this.model.on("create", this.createBrowser, this);
    this.model.on("zoomIn", this.zoomIn, this);
    this.model.on("zoomOut", this.zoomOut, this);
    this.model.on("toSVG", this.toSVG, this);
  }

  // State update methods
  locus_changed = () => {
    const browser = this.getBrowser(this.options.id)
    browser.search(this.model.get('locus'))
  }

  // RPC-like methods
  handle_custom_messages = (msg: ICustomMessage) => {
    const { type, ...obj } = msg;
    this.model.trigger(type, obj)
  }

  removeTrack = ({ name }: { name: string }) => {
    const browser = this.getBrowser(this.options.id)
    if (browser) {
      browser.removeTrackByName(name)
    }
  }

  loadTrack = ({ track }: { track: IBrowserTrack }) => {
    const browser = this.getBrowser(this.options.id)
    if (browser) {
      browser.loadTrack(track)
    }
  }

  loadGenome = ({ genome }: { genome: IBrowserGenome }) => {
    const browser = this.getBrowser(this.options.id)
    if (browser) {
      browser.loadGenome(genome)
    }
  }

  zoomIn = () => {
    const browser = this.getBrowser(this.options.id)
    if (browser) {
      browser.zoomIn()
    }
  }

  zoomOut = () => {
    const browser = this.getBrowser(this.options.id)
    if (browser) {
      browser.zoomOut()
    }
  }

  toSVG = () => {
    const browser = this.getBrowser(this.options.id)
    if (browser) {
      const svg = browser.toSVG()
      this.model.set('svg', svg)
      this.model.save_changes();
    }
  }

  // Browser instance management methods
  createBrowser = (div: HTMLElement) => {
    const id = this.options.id;
    if (igv.browserCache[id]) {
      console.log(`Browser for this ID (${id}) already exists`)
      return
    }
    igv.createBrowser(div, this.options)
      .then(function (browser: any) {
          igv.browserCache[id] = browser;
      })
  }

  removeBrowser = () => {
    if (document.getElementById(this.el)) {
      this.el.parentNode?.removeChild(this.el)
    }
    const id = this.options.id;
    if (igv.browserCache[id]) {
      delete igv.browserCache[id]
    }
  }

  getBrowser = (id: string) => {
    return igv.browserCache[id]
  }
  
  useBrowserMethod = (method: string) => {
    const browser = this.getBrowser(this.options.id)
    if (browser) {
      browser[method]()
    }
  }

}
