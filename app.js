


const {
    createBot,
    createProvider,
    createFlow,
    addKeyword } = require('@bot-whatsapp/bot')



const QRPortalWeb = require('@bot-whatsapp/portal')
const WebWhatsappProvider = require('@bot-whatsapp/provider/web-whatsapp')
const JsonFileAdapter = require('@bot-whatsapp/database/json')

// const {createBotDialog} = require('')
/**
 * Aqui declaramos los flujos hijos, los flujos se declaran de atras para adelante, es decir que si tienes un flujo de este tipo:
 *
 *          Menu Principal
 *           - SubMenu 1
 *             - Submenu 1.1
 *           - Submenu 2
 *             - Submenu 2.1
 *
 * Primero declaras los submenus 1.1 y 2.1, luego el 1 y 2 y al final el principal.
 */



const flowPrincipal = addKeyword(['hola', 'estoy aca', 'empecemos'])
    .addAnswer(['bienvenido al sistemas de asistencia virtual','el breve te enviamos la informacion'])
    .addAnswer('me regalas tu correo :', {capture:true},(ctx, {fallBack})=>{

        if(!ctx.body.includes('@')){
            return fallBack()
        }
        console.log('mensaje de entrada:',ctx.body)
    })


const flowsecundario = addKeyword(['gracias'])
    .addAnswer('de nada')
    .addAnswer('hoy tenemos ofertas')






const main = async () => {
    const adapterDB = new JsonFileAdapter()
    const adapterFlow = createFlow([flowPrincipal,flowsecundario])
    const adapterProvider = createProvider(WebWhatsappProvider)
    createBot({
        flow: adapterFlow,
        provider: adapterProvider,
        database: adapterDB,
    })
    QRPortalWeb()
}

main()
