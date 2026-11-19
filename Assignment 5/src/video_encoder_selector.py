"""Heuristic video encoding/upload selector (B4); estimates are illustrative."""
PROFILES={
 "budget_phone":{"cpu":0.7,"battery":22,"network_mbps":2.0,"camera_max":720},
 "midrange":{"cpu":1.2,"battery":58,"network_mbps":8.0,"camera_max":1080},
 "flagship":{"cpu":2.0,"battery":82,"network_mbps":25.0,"camera_max":2160},
 "wifi_low_battery":{"cpu":1.5,"battery":12,"network_mbps":80.0,"camera_max":2160},
}
OPTIONS=[(480,0.8),(720,1.8),(1080,4.0),(2160,12.0)]

def choose(p):
    max_res=p["camera_max"]
    if p["cpu"]<0.9 or p["battery"]<20:
        max_res=min(max_res,720)
    candidates=[(r,b) for r,b in OPTIONS if r<=max_res and b<=p["network_mbps"]*0.8]
    if not candidates: r,b=480,0.8
    else: r,b=candidates[-1]
    duration=20
    size_mb=b*duration/8
    upload_s=size_mb*8/p["network_mbps"]
    encode_energy=duration*(r/1080)*0.18/p["cpu"]
    radio_energy=upload_s*0.04
    energy=encode_energy+radio_energy
    remaining=max(0,p["battery"]-energy)
    timing="upload_now" if p["network_mbps"]>=5 and p["battery"]>=20 else "queue_until_unmetered_or_charging"
    return {"resolution":r,"bitrate_mbps":b,"upload_timing":timing,"estimated_upload_seconds":round(upload_s,1),"estimated_energy_units":round(energy,2),"battery_before":p["battery"],"estimated_battery_after":round(remaining,2)}

def main():
    for name,p in PROFILES.items():
        print(name,choose(p))
    print("challenge",{"profile":"custom_short_clip","heuristic":choose({"cpu":0.85,"battery":19,"network_mbps":40,"camera_max":2160}),"note":"heuristic caps at 720 because battery<20; for a 3-second clip, 1080 may fit the thermal/energy budget"})

if __name__=="__main__":
    main()
