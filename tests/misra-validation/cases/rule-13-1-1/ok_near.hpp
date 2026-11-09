// Near misses (near): virtual functions and multiple non-virtual bases, no virtual base.
#ifndef KV_RULE_13_1_1_OK_NEAR_HPP
#define KV_RULE_13_1_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_13_1_1::ok_near {

struct Id {
  std::uint32_t id = 0U;
};

struct Value {
  std::uint32_t value = 0U;
};

struct Sample : Id, Value {};

class Port {
 public:
  Port() = default;
  Port(const Port&) = delete;
  Port(Port&&) = delete;
  Port& operator=(const Port&) = delete;
  Port& operator=(Port&&) = delete;
  virtual ~Port() = default;
  virtual std::uint32_t read() const = 0;
};

inline std::uint32_t both(const Sample& s) { return s.id | s.value; }

}  // namespace kv::rule_13_1_1::ok_near

#endif  // KV_RULE_13_1_1_OK_NEAR_HPP
