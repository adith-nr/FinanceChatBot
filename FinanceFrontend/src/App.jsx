import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import ReactMarkdown from "react-markdown"
import './App.css'
import './ChatResponse.css'
function App() {

  const [prompt,setPrompt]=useState("")
  const [response,setResponse]=useState("")
  const [load,setLoad]=useState(false)
  
  const handelClick=async (e)=>{
    e.preventDefault()
    setLoad(true)
    const data = {"prompt":prompt}

    try {
      const res = await fetch("http://localhost:8000",{
        method:"POST",
        headers:{ "Content-Type": "application/json" },
        body:JSON.stringify(data)
      })

      const ans= await res.json()
      console.log(ans)
      setResponse(ans.response)


    } catch (error) {
      console.log("Error ",error)
    }
    setLoad(false)
  }

  return (
    <div className='container'>
      <h1 className='title'>Finance Agent</h1>
      <input type="text" placeholder='Enter Prompt' className='prompt' value={prompt} onChange={(e)=>{setPrompt(e.target.value)}} />
      <button onClick={handelClick} disabled={load}>Submit</button>
      <br />
      <br />
      {response ? (
        <div className='response-markdown'>
          <ReactMarkdown>{response}</ReactMarkdown>
        </div>
      ):(
        <h2>Tired of Browsing a 100 websites to analyze a stock,don't worry we gotcha!</h2>
      )}
      

    </div>
  )
}

export default App
