from CoreWLAN import (kCWSecurityDynamicWEP,
                      kCWSecurityEnterprise,
                      kCWSecurityModeDynamicWEP,
                      kCWSecurityModeOpen,
                      kCWSecurityModeWEP,
                      kCWSecurityModeWPA2_Enterprise,
                      kCWSecurityModeWPA2_PSK,
                      kCWSecurityModeWPA_Enterprise,
                      kCWSecurityModeWPA_PSK,
                      kCWSecurityModeWPS,
                      kCWSecurityNone,
                      kCWSecurityPersonal,
                      kCWSecurityUnknown,
                      kCWSecurityWEP,
                      kCWSecurityWPA2Enterprise,
                      kCWSecurityWPA2Personal,
                      kCWSecurityWPA3Enterprise,
                      kCWSecurityWPA3Personal,
                      kCWSecurityWPA3Transition,
                      kCWSecurityWPAEnterprise,
                      kCWSecurityWPAEnterpriseMixed,
                      kCWSecurityWPAPersonal,
                      kCWSecurityWPAPersonalMixed)


SECURITY_MODES = {kCWSecurityModeDynamicWEP: "Dynamic WEP",
                  kCWSecurityModeOpen: "Open",
                  kCWSecurityModeWEP: "WEP",
                  kCWSecurityModeWPA2_Enterprise: "WPA2 Enterprise",
                  kCWSecurityModeWPA2_PSK: "WPA2 Personal",
                  kCWSecurityModeWPA_Enterprise: "WPA Enterprise",
                  kCWSecurityModeWPA_PSK: "WPA Personal",
                  kCWSecurityModeWPS: "WPS"}

SECURITY_TYPES = {kCWSecurityDynamicWEP: "WEP/Dynamic",
                  kCWSecurityEnterprise: "WPA",
                  kCWSecurityNone: "Open",
                  kCWSecurityPersonal: "PSK",
                  kCWSecurityUnknown: "Unknown",
                  kCWSecurityWEP: "WEP",
                  kCWSecurityWPA2Enterprise: "WPA2",
                  kCWSecurityWPA2Personal: "WPA2 PSK",
                  kCWSecurityWPA3Enterprise: "WPA3",
                  kCWSecurityWPA3Personal: "WPA3",
                  kCWSecurityWPA3Transition: "WPA2/WPA3",
                  kCWSecurityWPAEnterprise: "WPA",
                  kCWSecurityWPAEnterpriseMixed: "WPA/Mix",
                  kCWSecurityWPAPersonal: "WPA PSK",
                  kCWSecurityWPAPersonalMixed: "WPA PSK/Mix"}
