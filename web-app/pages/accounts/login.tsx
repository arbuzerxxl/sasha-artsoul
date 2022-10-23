import type { NextPage } from 'next'
import { AuthWrapper } from '../../wrapper/AuthWrapper'
import { LoginLayout } from '../../layout/LoginLayout'

const Home: NextPage = () => {
  return (
    <AuthWrapper>
      <LoginLayout />
    </AuthWrapper>
  )
}

export default Home
