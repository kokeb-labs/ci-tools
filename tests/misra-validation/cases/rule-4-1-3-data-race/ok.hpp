// Compliant: the same task without the undefined behaviour.
#ifndef KV_RULE_4_1_3_DATA_RACE_OK_HPP
#define KV_RULE_4_1_3_DATA_RACE_OK_HPP

#include <cstdint>

namespace kv::rule_4_1_3_data_race::ok {

inline std::uint32_t bump(std::uint32_t counter) { return counter | 1U; }

}  // namespace kv::rule_4_1_3_data_race::ok

#endif  // KV_RULE_4_1_3_DATA_RACE_OK_HPP
