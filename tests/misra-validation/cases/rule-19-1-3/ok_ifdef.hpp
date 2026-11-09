// Near miss: #ifdef and #ifndef of undefined identifiers evaluate nothing.
#ifndef KV_RULE_19_1_3_OK_IFDEF_HPP
#define KV_RULE_19_1_3_OK_IFDEF_HPP

#include <cstdint>

namespace kv::rule_19_1_3::ok_ifdef {

#ifdef KV_RULE_19_1_3_NEVER
constexpr std::uint8_t kFlag = 1U;
#else
constexpr std::uint8_t kFlag = 0U;
#endif

}  // namespace kv::rule_19_1_3::ok_ifdef

#endif  // KV_RULE_19_1_3_OK_IFDEF_HPP
