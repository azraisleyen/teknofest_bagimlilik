export class LocationResolver{
  static radians(value){return value*Math.PI/180}
  static distanceKm(point,center){const dLat=this.radians(center.latitude-point.latitude),dLon=this.radians(center.longitude-point.longitude),lat1=this.radians(point.latitude),lat2=this.radians(center.latitude);const h=Math.sin(dLat/2)**2+Math.cos(lat1)*Math.cos(lat2)*Math.sin(dLon/2)**2;return 6371.0088*2*Math.asin(Math.sqrt(h))}
  static nearest(point,centers){return centers.map(center=>({center,km:this.distanceKm(point,center)})).sort((a,b)=>a.km-b.km)[0]||null}
}
