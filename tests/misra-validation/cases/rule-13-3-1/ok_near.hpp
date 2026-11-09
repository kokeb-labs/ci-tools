// Near misses (near): final on its own marks an overrider.
#ifndef KV_RULE_13_3_1_OK_NEAR_HPP
#define KV_RULE_13_3_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_13_3_1::ok_near {

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

class Fake : public Port {
 public:
  Fake() = default;
  Fake(const Fake&) = delete;
  Fake(Fake&&) = delete;
  Fake& operator=(const Fake&) = delete;
  Fake& operator=(Fake&&) = delete;
  ~Fake() override = default;
  std::uint32_t read() const final { return 3U; }
};

inline std::uint32_t sample(const Port& p) { return p.read(); }

}  // namespace kv::rule_13_3_1::ok_near

#endif  // KV_RULE_13_3_1_OK_NEAR_HPP
