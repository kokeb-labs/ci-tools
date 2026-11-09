// Compliant: __has_include is standard since C++17, and #ifdef treats it as a defined macro
// (Rule 4.1.1); the operand of __has_include is a header name, not identifiers (Rule 19.1.3).
#ifndef KV_HAS_INCLUDE_OK_HPP
#define KV_HAS_INCLUDE_OK_HPP

#ifdef __has_include
#if __has_include("kv_absent_config.h")
#include "kv_absent_config.h"
#endif
#endif

#ifndef KV_DEFAULT_TIMEOUT_US
#define KV_DEFAULT_TIMEOUT_US 10000
#endif

#endif  // KV_HAS_INCLUDE_OK_HPP
