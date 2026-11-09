// Compliant: only standard escape sequences.
#ifndef KV_RULE_5_13_1_OK_HPP
#define KV_RULE_5_13_1_OK_HPP

namespace kv::rule_5_13_1::ok {

inline const char* path() { return "dir\\file\n"; }

}  // namespace kv::rule_5_13_1::ok

#endif  // KV_RULE_5_13_1_OK_HPP
