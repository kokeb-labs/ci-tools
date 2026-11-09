// Compliant: no cast; the function takes what it writes as non-const.
#ifndef KV_RULE_8_2_3_OK_HPP
#define KV_RULE_8_2_3_OK_HPP

#include <cstdint>

namespace kv::rule_8_2_3::ok {

inline void reset(std::uint32_t* reg) { *reg = 0U; }

}  // namespace kv::rule_8_2_3::ok

#endif  // KV_RULE_8_2_3_OK_HPP
