// Compliant: the function pointer keeps its own type.
#ifndef KV_RULE_8_2_4_OK_HPP
#define KV_RULE_8_2_4_OK_HPP

#include <cstdint>

namespace kv::rule_8_2_4::ok {

inline std::int32_t handler(std::int32_t code) { return code; }

using Handler = std::int32_t (*)(std::int32_t);

inline Handler table_entry() { return &handler; }

}  // namespace kv::rule_8_2_4::ok

#endif  // KV_RULE_8_2_4_OK_HPP
