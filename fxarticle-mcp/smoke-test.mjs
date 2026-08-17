import { spawn } from "node:child_process";
const p = spawn("node", ["dist/index.js"], { stdio: ["pipe","pipe","pipe"] });
let buf = ""; const pending = new Map();
p.stdout.on("data", d => { buf += d;
  let i; while ((i = buf.indexOf("\n")) >= 0) { const line = buf.slice(0,i); buf = buf.slice(i+1);
    if (!line.trim()) continue; const msg = JSON.parse(line);
    if (pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); } } });
let id = 0;
const send = (method, params) => new Promise(res => { const _id = ++id;
  pending.set(_id, res); p.stdin.write(JSON.stringify({jsonrpc:"2.0", id:_id, method, params})+"\n"); });

await send("initialize", {protocolVersion:"2024-11-05", capabilities:{}, clientInfo:{name:"probe",version:"1"}});
p.stdin.write(JSON.stringify({jsonrpc:"2.0",method:"notifications/initialized"})+"\n");

const tools = await send("tools/list", {});
console.log("TOOLS:", tools.result.tools.map(t=>t.name).join(", "));

const call = async (name, args) => (await send("tools/call", {name, arguments: args})).result;

console.log("\n=== 1. fetch article (the user's link) ===");
let r = await call("x_fetch_article", {url_or_id:"https://x.com/startupideaspod/status/2087661842231664780?s=12"});
console.log(r.content[0].text.slice(0, 1400));
console.log("\n[structured]", JSON.stringify({...r.structuredContent, markdown:"<omitted>"}, null, 1));

console.log("\n=== 2. list articles ===");
r = await call("x_list_articles", {handle:"@startupideaspod", limit:3});
console.log(r.content[0].text.slice(0,700));

console.log("\n=== 3. non-article post ===");
r = await call("x_fetch_post", {url_or_id:"2086195748656599254", mode:"thread"});
console.log(r.content[0].text.slice(0,500));

console.log("\n=== 4. error handling: bad id ===");
r = await call("x_fetch_article", {url_or_id:"1111111111111111111"});
console.log("isError:", r.isError, "|", r.content[0].text);

console.log("\n=== 5. error handling: garbage input ===");
r = await call("x_fetch_article", {url_or_id:"not a tweet"});
console.log("isError:", r.isError, "|", r.content[0].text);
p.kill();
