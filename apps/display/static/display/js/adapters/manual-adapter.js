export class ManualSimulationAdapter{start(onSignal){this.callback=onSignal}emit(signal){this.callback?.(signal)}stop(){this.callback=null}}
