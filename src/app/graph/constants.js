export const baseUrl = window.location.pathname.match(/.*(?:base|clean)\//)[0]
export const baseGraphName = window.location.pathname.match(/\/([^\/]*)\/$/)[1]