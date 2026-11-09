// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_4_2_VIRTUAL_OK_NEAR_HPP
#define KV_RULE_6_4_2_VIRTUAL_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_4_2_virtual::near {

class Sink {
 public:
  Sink() = default;
  Sink(const Sink&) = delete;
  Sink(Sink&&) = delete;
  Sink& operator=(const Sink&) = delete;
  Sink& operator=(Sink&&) = delete;
  virtual ~Sink() = default;
  virtual void put(std::int32_t value) = 0;
  virtual void put(std::int32_t value, std::int32_t weight) = 0;
};
// Overrides one overload and brings the other into scope with a using-declaration: nothing hidden.
class Logger : public Sink {
 public:
  Logger() = default;
  Logger(const Logger&) = delete;
  Logger(Logger&&) = delete;
  Logger& operator=(const Logger&) = delete;
  Logger& operator=(Logger&&) = delete;
  ~Logger() override = default;
  using Sink::put;
  void put(std::int32_t value) override;
};

}  // namespace kv::rule_6_4_2_virtual::near

#endif  // KV_RULE_6_4_2_VIRTUAL_OK_NEAR_HPP
