package API_Tests;

import io.gatling.javaapi.core.ScenarioBuilder;
import io.gatling.javaapi.core.Simulation;
import io.gatling.javaapi.http.HttpProtocolBuilder;

import static io.gatling.javaapi.core.CoreDsl.*;
import static io.gatling.javaapi.http.HttpDsl.http;
import static io.gatling.javaapi.http.HttpDsl.status;

public class MessageTest extends Simulation {

    //protocol
    private HttpProtocolBuilder httpProtocol = http
            .baseUrl("http://localhost:8000");

    private ScenarioBuilder MessageTest = scenario("Message Test").exec(
            http("Send message")
                    .post("/messages/test").header("content-type","application/json")
                    .asJson()
//                    .body(RawFileBody("Data/user.json"))
                    .body(StringBody("{\"message\": \"privetsber\"}")).asJson()
                    .check(status().is(201),jsonPath("$.detail").is("Message sent to Kafka"))).pause(1);

    {
        setUp(
                MessageTest.injectOpen(rampUsers(10).during(5)).protocols(httpProtocol));
    }
}
