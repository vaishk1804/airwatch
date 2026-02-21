export type Location = {
  id:number;
  name:string;
  state?:string | null;
  country: string;
  lat: number;
  lon:number;
};