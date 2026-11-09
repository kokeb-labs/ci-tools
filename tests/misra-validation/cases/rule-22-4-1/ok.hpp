// Compliant: errno is only reset to zero before a call that may set it.
#ifndef KV_RULE_22_4_1_OK_HPP
#define KV_RULE_22_4_1_OK_HPP

#include <cerrno>

namespace kv::rule_22_4_1::ok {

inline void clear_error() { errno = 0; }

}  // namespace kv::rule_22_4_1::ok

#endif  // KV_RULE_22_4_1_OK_HPP
