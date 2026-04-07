import ImageUpload from '../components/ImageUpload'

export default function Identify() {
  return (
    <div>
      <ImageUpload label="Front of card" testId="front" onFile={() => {}} />
    </div>
  )
}
