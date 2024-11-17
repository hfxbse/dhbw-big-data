import styles from './Footer.module.css';

export default function Footer() {
    return <div className={styles.license}>
        <a rel="license" href="https://creativecommons.org/licenses/by-sa/4.0/" style={{height: '15px'}}>
            <img alt="Creative Commons License" style={{borderWidth: 0}} src="/ccbysa_4.0.png"/>
        </a>
        <div>
            <span xmlns:dct="http://purl.org/dc/terms/" property="dct:title">
                <a
                    xmlns:cc="https://creativecommons.org/ns#"
                    href="https://opencellid.org"
                    property="cc:attributionName"
                    rel="cc:attributionURL"
                >
                    OpenCelliD Project&nbsp;
                </a>
            </span>
            <a
                xmlns:cc="https://creativecommons.org/ns#"
                href="https://opencellid.org"
                property="cc:attributionName"
                rel="cc:attributionURL">
            </a>
            is licensed under a&nbsp;
            <a rel="license" href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank">
                Creative Commons Attribution-ShareAlike 4.0 International License
            </a>
        </div>
    </div>
}