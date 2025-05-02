package experimenting14_go_pong

const (
	left  = iota
	right = iota
)

type paddle struct {
	direction int
}

type ball struct{}

type TransformComponent struct {
	position [2]float64
	velocity [2]float64
	angle    [2]float64
}
type SizeComponent struct {
	size int
}

type angle float64

func (b *ball) getVelocityAngle() angle {
	// do something
	return 0.0 // placeholder
}

func (p *paddle) updatePaddle() {

}

func (b *ball) updateBall() {

}

func main() {
	// init video stuff

	//
}
