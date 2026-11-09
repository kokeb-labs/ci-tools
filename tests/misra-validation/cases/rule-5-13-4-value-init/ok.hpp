// Compliant: value-initialisation of a class whose members have default member initialisers; no
// unsuffixed literal of unsigned type appears (0 is an int literal, 0U carries its suffix).
#ifndef KV_RULE_5_13_4_VALUE_INIT_OK_HPP
#define KV_RULE_5_13_4_VALUE_INIT_OK_HPP

#include <cstdint>

namespace kv::rule_5_13_4_value_init::ok {

struct Timing {
  std::uint32_t clock_hz{0U};
  std::uint16_t raw{0};
};

inline Timing defaults() { return Timing{}; }

inline bool idle(const Timing& t) { return (t.clock_hz == 0U) && (t.raw == 0U); }

}  // namespace kv::rule_5_13_4_value_init::ok

#endif  // KV_RULE_5_13_4_VALUE_INIT_OK_HPP
