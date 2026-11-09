#ifndef KV_RULE_7_0_3_OK_HPP
#define KV_RULE_7_0_3_OK_HPP

// Compliant: characters are only compared with other characters.
namespace kv::rule_7_0_3::ok {

inline bool is_separator(char c) { return (c == ',') || (c == ';'); }

}  // namespace kv::rule_7_0_3::ok

#endif  // KV_RULE_7_0_3_OK_HPP
