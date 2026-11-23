import React from 'react'
import Ipc from '../lib/ipc'
import Image from 'next/image'

import Card from '../components/ui/card'
import Button from './ui/button'
import Loader from './ui/loader'

import { useTranslation } from 'react-i18next'

interface AuthProps {
  signedIn: boolean;
  deviceCode?: {code:string;url:string} | null;
  gamertag?: string;
  gamerpic?: string;
  gamerscore?: string;
  isLoading?: boolean;
}

function Auth({
    signedIn = false,
    deviceCode = null,
    gamertag,
    gamerpic,
    gamerscore,
    isLoading = false,
}: AuthProps) {
    const { t } = useTranslation()

    function startAuthFlow(){
        Ipc.send('app', 'login')
    }

    function logout(){
        if(confirm(t('auth.logoutQuestion'))){
            Ipc.send('app', 'clearData')
        }
    }

    function clearData(){
        if(confirm(t('auth.clearDataQuestion'))){
            Ipc.send('app', 'clearData')
        }
    }

    return (
        <React.Fragment>
            <div id="component_auth">

                <div id="component_auth_modal">
                    { deviceCode ? <Card><h1>Sign in on your phone or computer</h1><p>Open {deviceCode.url}</p><p style={{fontSize:48,letterSpacing:6}}>{deviceCode.code}</p><p>Greenlight will continue automatically.</p></Card> : isLoading === false ?
                        <Card>
                            {signedIn === true ? (<div className="component_auth_profile_container">
                                <div className="component_auth_profile_gamerpic">
                                    <Image src={ gamerpic } className="component_auth_profile_gamerpic_img" alt={ gamertag } width='96' height='96'></Image>
                                </div>

                                <div className="component_auth_profile_userdetails">
                                    <h1>{ gamertag }</h1>
                                    <p>
                                        {t('auth.gamerscore')}: { gamerscore }
                                    </p>
                                    {/* <p>
                                        {t('auth.loggingIn')}
                                    </p> */}
                                    <Button label={t('auth.loginBtn')} className='btn-primary' onClick={ () => {
                                        startAuthFlow()
                                    } }></Button> &nbsp;
                                    <Button label={t('auth.logoutBtn')} className='btn' onClick={ () => {
                                        logout()
                                    } }></Button>
                                </div>

                            </div>) : (<div style={{
                                textAlign: 'center',
                                paddingBottom: '20px',
                            }}>
                                <h1>{t('auth.loginWithXbox')}</h1>
                                <p>
                                    {t('auth.pleaseAuthenticate')}
                                </p>
                                <Button label={t('auth.loginBtn')} className='btn-primary' onClick={ () => {
                                    startAuthFlow()
                                } }></Button> &nbsp;
                                <Button label={t('auth.clearDataBtn')} className='btn' onClick={ () => {
                                    clearData()
                                } }></Button>
                            </div>) }
                        </Card>:<Card><div style={{
                            textAlign: 'center',
                        }}><Loader></Loader><br /></div></Card>
                    }
                </div>
            </div>
        </React.Fragment>
    )
}

export default Auth
